# A KiCad DocSet

This is a docset for KiCad source code. This should be compatible with [Zeal][].

## Feeds

Generally, you can just add the relevant feed from the current Git HEAD,
which will refer to the most recent docset. If you want a feed for a specific
version, they are also archive in the releases.

These are the current feeds, which will update as new versions are released:

* Main development branch docs:
    * `master`: https://raw.githubusercontent.com/johnbeard/kicad-docset/master/feeds/master/KiCad.xml
* Stable release (5.1) docs:
    * `master`: https://raw.githubusercontent.com/johnbeard/kicad-docset/master/feeds/5.1/KiCad.xml

You can also download and extract the docset from the TGZ file in each release yourself.
There are under the Github releases, you do not need to bother with the tarballs of this
repo's code.

## Icons

For some reason, the icon in the TGZ is not found by Zeal. You can
use this one: ![KiCad
logo](https://github.com/johnbeard/kicad-docset/raw/master/icons/icon.png)
(which is the KiCad website's
[favicon](http://kicad-pcb.org/favicon-16x16.png)).

Save it as `icon.png` in the unpacked docset (e.g. `~/.local/share/Zeal/Zeal/docsets/KiCad.docset`).

Or, use the following command (but don't get too used to running commands you find on the Internet, they can be [evil](https://thejh.net/misc/website-terminal-copy-paste)).

```
curl -o ~/.local/share/Zeal/Zeal/docsets/KiCad.docset/icon.png https://github.com/johnbeard/kicad-docset/raw/master/icons/icon.png
```

## Updates

These docsets are not updated automatically when KiCad changes.
If you need a new release, and none seems forthcoming, open an issue.

In future, perhaps these can be provided by the KiCad CI services automatically.
If that happens, there will be a new feed URL to use.

## Build your own

To build your own docset, you do not need this repo, which exists only to
upload pre-made releases via Github.

You should clone the [main KiCad repo][] and then build the `docset` target.

[Zeal]: https://zealdocs.org
[main KiCad repo]: https://code.launchpad.net/kicad
