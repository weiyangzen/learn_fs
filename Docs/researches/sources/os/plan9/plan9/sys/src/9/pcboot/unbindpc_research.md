# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/unbindpc

This is an `rc` helper script for unbinding pcboot files that were mounted or overlaid from related `pc` build directories.

Key responsibilities:
- Exits quietly if expected local files are absent.
- Uses `rfork e`.
- Unmounts matching `pc?*pxe` entries without dots.
- Unmounts the current mount, `/tmp/blank`, and exits successfully.

Filesystem/storage relevance:
- Build/workspace helper only; it affects source-tree namespace setup, not runtime filesystem behavior.
