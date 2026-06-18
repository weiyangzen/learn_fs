# File Research: sources/local-fs/btrfs-progs/cmds/inspect-dump-super.c

## Purpose
Implements `btrfs inspect-internal dump-super`, which reads and prints one or more superblock copies from devices or filesystem image files.

## Core Logic
- `load_and_dump_sb()` stats the input, avoids reading beyond the end for block/regular files, reads the superblock at a requested bytenr, validates magic unless forced, and delegates formatting to `btrfs_print_superblock()`.
- `cmd_inspect_dump_super()` parses `--full`, `--all`, `--super`, `--force`, and `--bytenr`, plus deprecated `-i` and legacy `-s <bytenr>` behavior.

## CLI Behavior
`--all` iterates all standard superblock mirror offsets. A specific `--super` mirror or `--bytenr` clears all-mode. Multiple devices are processed sequentially.

## Error Handling
Reports open/stat/read failures, short reads, bad magic without force, and invalid mirror indexes. Short devices that have no later superblock copy can silently skip that copy.
