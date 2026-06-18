# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/conf.c

## Purpose
Parses `plan9.ini` or PXE configuration, supports boot menus, manages boot arguments in low memory, reads BIOS-provided memory/APM tables, and provides configuration lookup/prompting for the bootstrap.

## Main Interfaces
- Exports `getstr`, `askbootfile`, `isconf`, `getconf`, `readlsconf`, `addconf`, `changeconf`, and `dotini`.
- Defines global `Chan *conschan`.

## Implementation Notes
- `getstr` prompts on `#c/cons`, supports default values, timeout defaults, and queued-key detection through `kbdq`.
- Menu parsing recognizes `[menu]`, `menuitem=`, `menudefault=`, and `menuconsole=`, then rewrites the active config into `BOOTARGS`.
- `readlsconf` parses low-memory records written by real-mode assembly: `APM\0` records are skipped here, `MAP\0` records populate `mmap`.
- `dotini` normalizes line endings, spaces, comments, blank lines, and tabs before menu parsing and `name=value` extraction.
- Boot args are stored at `CONFADDR`, with an `id` prefix unless already present.
- `changeconf` deletes an existing matching key line and appends a replacement.

## Dependencies And Risks
- Global arrays have `MAXCONF` capacity and only warn for too many lines.
- `getconf` prompts if a key has multiple values.
- Menu parsing mutates the input buffer and uses global menu state.
