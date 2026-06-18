# File Research: sources/os/bsd/freebsd-src/sbin/bsdlabel/pathnames.h

## Purpose
Path constants for `bsdlabel`.

## Main Elements
- Includes `<paths.h>`.
- Defines `_PATH_BOOTDIR` as `/boot`.
- Defines `PATH_TMPFILE` as `/tmp/EdDk.XXXXXXXXXX`.

## Dependencies And Integration
`bsdlabel.c` uses `PATH_TMPFILE` for editor-backed label edits. `_PATH_BOOTDIR` documents boot path convention, though the source directly defaults boot code to `/boot/boot`.

## Risk Notes
Tempfile path affects where editable disklabel prototypes are created.
