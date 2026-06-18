# File Research: sources/virtualization/nbdkit/plugins/floppy/directory-lfn.c

This file implements FAT directory table creation for the floppy plugin, with most of the complexity centered on VFAT long filename handling.

Key behavior:
- `create_directory` builds each directory's on-disk `dir_entry` vector, adding a root volume label or subdirectory `.`/`..` entries first.
- It converts every child directory and file name in a directory before emitting entries so 8.3 short-name collisions can be resolved across the whole directory.
- `add_directory_entry` emits the VFAT LFN entries in reverse sequence order, followed by the 8.3 entry with attributes, timestamps, size, and deferred cluster fields.
- `update_directory_first_cluster` later patches cluster numbers after `virtual-floppy.c` has assigned clusters to all directories/files.

Important implementation details:
- Long names are converted from UTF-8 to UTF-16LE with `iconv`, using `//TRANSLIT` under GNU libc.
- Short names are built from an ASCII allowlist, uppercased, and duplicate names are renamed using a `~<index>` suffix.
- FAT timestamps are derived from local `stat` times and packed into FAT date/time fields.
- LFN entries are detected by attribute `0x0f`; root volume labels and `.`/`..` are skipped when patching normal file/directory cluster references.

Dependencies:
- Uses structures and constants from `virtual-floppy.h`.
- Uses `dir_entries_append`, `floppy->dirs`, and `floppy->files` populated by `virtual-floppy.c`.

Risks and edge cases:
- The code assumes the current locale/input filenames are UTF-8.
- Short-name collision handling is O(n^2) and simple; comments acknowledge this.
- `pad_string` truncates labels/names without validation.
- The cluster patcher relies on the exact order in which directory entries were emitted.
