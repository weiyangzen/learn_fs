# File Research: sources/local-fs/ocfs2-tools/fswreck/main.c

This is the `fswreck` command-line entry point and corruption-code registry.

Key structures:
- Global `progname`, `device`, selected `slotnum`, and `corrupt[NUM_FSCK_TYPE]`.
- `struct prompt_code` binds enum code, string name, required mkfs feature string, slot count, corruption function, and description.
- `prompt_codes[]` is indexed by `enum fsck_type` and defines all supported corruption codes, including unimplemented `LALLOC_REPAIR` and `LALLOC_USED` entries with NULL handlers.

CLI behavior:
- `-c` parses comma-separated corruption names.
- `-C` selects corruption by number.
- `-L` prints the string for a selected numeric code.
- `-l` lists all codes and descriptions.
- `-n` prints `NUM_FSCK_TYPE`.
- `-M` prints suggested mkfs options for the selected corruption, including required slots and feature toggles.
- `-N` selects a slot number.

Runtime flow:
- Initializes OCFS error table and signal handlers.
- Parses options, opens the target device read-write with `ocfs2_open()`.
- Iterates all selected corruption codes, skips NULL handlers with a message, and invokes each function.
- Closes the filesystem before returning.

Integration notes:
- This file must stay synchronized with `fsck_type.h` and implementation dispatchers in `corrupt.c`.
- The tool is intentionally destructive and prints a prominent warning in usage text.
