# File Research: sources/local-fs/dosfstools/src/boot.h

Public interface for FAT boot-sector and label operations.

Declared functions:
- `read_boot()` initializes a `DOS_FS` from the open filesystem.
- `write_label()`, `write_boot_label()`, `write_volume_label()`, `remove_label()`, and `write_serial()` mutate label/serial metadata.
- `find_volume_de()` locates the root-directory volume-label entry.
- `pretty_label()` formats an 11-byte DOS label for display.
- `alloc_rootdir_entry()` allocates a root-directory slot, optionally generating a unique name.

Role:
- Exposes boot/layout parsing and root-label manipulation to `fsck.fat`, `fatlabel`, `fat.c`, and checker repair code.
