# File Research: sources/os/plan9/plan9/sys/src/9/port/devkbmap.c

Implements `#κ/kbmap`, a privileged keyboard map inspection and update device. Only `eve` may open it.

Reads return fixed-width text records of keyboard map entries: map/table id, scan code, and resulting rune. Offsets are interpreted in units of `KBLINELEN`, so random-access reads can target map entries.

Writes parse newline-delimited mapping records. Accepted rune forms include quoted characters, control notation like `^X`, mouse/function pseudo-runes `M1` through `M5`, and numeric values. Blank/comment lines are ignored. Partial trailing lines are saved in `c->aux` and completed by later writes.

Parsed mappings are applied through `kbdputmap(map, key, rune)`. This file is a user-facing control surface for the kernel keyboard translation tables.
