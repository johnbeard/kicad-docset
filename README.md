# A KiCad DocSet

This is a docset for KiCad source code. This should be compatible with [Zeal][].

## Feeds

Generally, you can just add the relevant feed from the current Git HEAD,
which will refer to the most recent docset. If you want a feed for a specific
version, they are also archive in the releases.

These are the current feeds, which will update as new versions are released:

* Main docs
    * `master`: https://raw.githubusercontent.com/johnbeard/kicad-docset/master/feeds/master/KiCad.xml

You can also download and extract the docset from the TGZ file yourself.

Under the Github releases, you do not need to bother with the tarballs of this
repo's code.

## Icons

For some reason, the icon in the TGZ is not found by Zeal. You can
use this one: http://kicad-pcb.org/favicon-16x16.png

Save it as `icon.png` in the unpacked docset (e.g. `~/.local/share/Zeal/Zeal/docsets/KiCad.docset`).

## Updates

These docsets are not updated automatically when KiCad changes.
If you need a new release, and none seems forthcoming, open an issue.

In future, perhaps these can be provided by the KiCad CI services automatically.
If that happens, there will be a new feed URL to use.

[Zeal]: https://zealdocs.org

