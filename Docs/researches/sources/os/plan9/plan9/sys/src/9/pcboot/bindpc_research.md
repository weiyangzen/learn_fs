# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/bindpc

## Purpose
Plan 9 `rc` helper script to bind files from sibling `../pc` into a boot build directory and create suffixed stub bindings.

## Main Interfaces
- Invoked as `bindpc pfx sfx`.
- Uses Plan 9 commands `rfork`, `bind`, `ls`, `grep`, and `aux/stub`.

## Implementation Notes
- Exits early if `etherigbe.c` already exists, avoiding repeated setup.
- Deduces current boot directory name and binds it copy-before-change.
- Finds files matching prefix but excluding dotted files, `mkfile`, and existing suffixes.
- Creates blank stub files in `/tmp/blank`, binds them into the current directory, then binds real files over suffixed names.
- Finally binds `../pc` into the boot directory.

## Dependencies And Risks
- Plan 9 namespace script, not portable shell.
- Uses `/tmp/blank` as a shared staging path.
- Existing-file early exit may skip updates if stale bindings are present.
