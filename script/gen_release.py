#!/usr/bin/env python3
"""Generate and upload KiCad docset releases to GitHub."""

import argparse
import logging
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

log = logging.getLogger(__name__)

FEED_NAME = "KiCad"
GH_OWNER = "johnbeard"
GH_PROJ = "kicad-docset"
GH_URL = f"https://github.com/{GH_OWNER}/{GH_PROJ}"
GH_API_URL = "https://api.github.com"
GH_UPLOAD_URL = "https://uploads.github.com"

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and upload a KiCad docset release.",
    )
    parser.add_argument("branch", help="The release branch")
    parser.add_argument("docset", type=Path, help="Path to pre-generated docset")
    parser.add_argument(
        "-n", "--dryrun", action="store_true", help="Do not perform the upload"
    )
    return parser.parse_args()


def read_token() -> str:
    token_file = REPO_ROOT / "access_token.txt"
    return token_file.read_text().strip()


def get_version(docset: Path) -> str:
    """Extract the version string from the docset's Info.plist."""
    plist = docset / "Contents" / "Info.plist"
    tree = ET.parse(plist)
    root = tree.getroot()

    dict_elem = root.find(".//dict")
    if dict_elem is None:
        raise ValueError("No <dict> element in plist")

    children = list(dict_elem)
    for i, child in enumerate(children):
        if child.tag == "key" and child.text == "CFBundleVersion":
            version = children[i + 1].text or ""
            # Strip -dirty suffix
            return re.sub(r"-dirty$", "", version).strip()

    raise ValueError("CFBundleVersion not found in plist")


def create_tarball(docset: Path) -> Path:
    """Create a .tgz archive of the docset."""
    tar_path = REPO_ROOT / "docsets" / f"{FEED_NAME}.tgz"
    tar_path.parent.mkdir(parents=True, exist_ok=True)

    docset = docset.resolve()
    log.info("Creating tarball %s from %s", tar_path, docset)

    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(docset, arcname=docset.name, filter=_exclude_ds_store)
    return tar_path


def _exclude_ds_store(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    if Path(info.name).name == ".DS_Store":
        return None
    return info


def _release_tag(branch: str, version: str) -> str:
    """Return the GitHub release tag for a given branch."""
    if branch == "master":
        return "master"
    return version


def write_feed(branch: str, version: str) -> Path:
    """Write the Dash feed XML file."""
    tar_name = f"{FEED_NAME}.tgz"
    tag = _release_tag(branch, version)
    release_url = f"{GH_URL}/releases/download/{tag}/{tar_name}"

    feed_dir = REPO_ROOT / "feeds" / branch
    feed_dir.mkdir(parents=True, exist_ok=True)
    feed_file = feed_dir / f"{FEED_NAME}.xml"

    entry = ET.Element("entry")
    ET.SubElement(entry, "name").text = FEED_NAME
    ET.SubElement(entry, "version").text = version
    ET.SubElement(entry, "url").text = release_url

    tree = ET.ElementTree(entry)
    ET.indent(tree, space="    ")
    tree.write(feed_file, xml_declaration=False, encoding="unicode")
    # Ensure trailing newline
    with open(feed_file, "a") as f:
        f.write("\n")

    log.info("Wrote feed: %s", feed_file)
    return feed_file


def git_commit_feed(feed_file: Path, branch: str, version: str) -> None:
    rel = feed_file.relative_to(REPO_ROOT)

    subprocess.run(
        ["git", "add", str(rel)],
        cwd=REPO_ROOT,
        check=True,
    )

    # Only commit if there are staged changes (feed content may be unchanged)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
    if result.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", f"Updating feed: {branch} -> {version}"],
            cwd=REPO_ROOT,
            check=True,
        )
    else:
        log.info("Feed unchanged, skipping commit")


class GithubReleaser:
    """Manage GitHub releases for the docset repository."""

    def __init__(
        self, token: str, branch: str, version: str, *, dry_run: bool = False
    ) -> None:
        self.branch = branch
        self.version = version
        self.dry_run = dry_run
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
            }
        )
        self._rel_url = f"{GH_API_URL}/repos/{GH_OWNER}/{GH_PROJ}/releases"
        self._upload_url = f"{GH_UPLOAD_URL}/repos/{GH_OWNER}/{GH_PROJ}"

    @property
    def tag(self) -> str:
        """The GitHub release tag.

        For master, use a fixed 'master' tag so there is a single rolling
        release.  For stable branches, use the actual version string.
        """
        if self.branch == "master":
            return "master"
        return self.version

    @property
    def is_rolling(self) -> bool:
        return self.branch == "master"

    def get_or_create_release(self) -> int:
        """Return the release ID, creating the release if necessary."""
        resp = self._session.get(f"{self._rel_url}/tags/{self.tag}")

        if resp.status_code == 404:
            if self.dry_run:
                log.info("Dry run: would create release: %s", self.tag)
                return 4242
            log.info("Creating release: %s", self.tag)
            data = {
                "tag_name": self.tag,
                "target_commitish": "master",
                "name": self.tag,
                "body": "",
                "prerelease": self.is_rolling,
            }
            resp = self._session.post(self._rel_url, json=data)
            resp.raise_for_status()
        else:
            resp.raise_for_status()
            log.info("Release already exists: %s", self.tag)

        return resp.json()["id"]

    def delete_release_assets(self, release_id: int) -> None:
        """Delete all existing assets on a release."""

        if self.dry_run:
            log.info("Dry run: would delete existing assets for release ID %d", release_id)
            return

        url = f"{self._rel_url}/{release_id}/assets"
        resp = self._session.get(url)
        resp.raise_for_status()
        for asset in resp.json():
            log.info("Deleting old asset: %s", asset["name"])
            self._session.delete(asset["url"]).raise_for_status()

    def upload_asset(self, release_id: int | None, filepath: Path) -> None:
        if self.dry_run:
            log.info("Dry run: would upload %s", filepath)
            return
        log.info("Uploading %s", filepath)
        url = f"{self._upload_url}/releases/{release_id}/assets"
        with open(filepath, "rb") as f:
            self._session.post(
                url,
                params={"name": filepath.name},
                headers={"Content-Type": "application/octet-stream"},
                data=f,
            ).raise_for_status()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()

    version = get_version(args.docset)
    log.info("Doc version: %s", version)

    tar_path = create_tarball(args.docset)
    feed_file = write_feed(args.branch, version)

    token = read_token()
    gh = GithubReleaser(token, args.branch, version, dry_run=args.dryrun)

    release_id = gh.get_or_create_release()
    log.info("Release ID: %d", release_id)

    if gh.is_rolling:
        # Rolling release: remove old assets before re-uploading
        gh.delete_release_assets(release_id)

    gh.upload_asset(release_id, tar_path)
    gh.upload_asset(release_id, feed_file)

    git_commit_feed(feed_file, args.branch, version)

    log.info("Done")


if __name__ == "__main__":
    main()
