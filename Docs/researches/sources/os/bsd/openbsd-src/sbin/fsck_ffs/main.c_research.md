# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/main.c

## Scope

Top-level driver and global state owner for OpenBSD `fsck_ffs`. It parses command-line options, initializes signal handling, invokes setup, runs the five FFS check phases, reports summary statistics, writes superblocks if needed, and handles root-filesystem post-repair behavior.

## Main APIs And State

- `main()` handles `-p`, `-b`, `-c`, `-d`, `-f`, `-m`, `-n`, `-y`, initializes `checkroot()`, `catchinfo()`, and dispatches one filesystem through `checkfilesys()`.
- `argtoi()` parses numeric options with strict trailing-character rejection.
- `checkfilesys()` is the main repair sequence.
- Defines central globals shared by `fsck_ffs`: buffer heads, superblock buffers, duplicate-block list, zero-link list, inode state tables, block map, file counters, file descriptors, flags, and lost+found inode.

## Control Flow

`checkfilesys()` calls `setup()`, skips clean filesystems when allowed, initializes `resolved`, then runs:

1. `pass1()` for inode/block scan.
2. `pass1b()` when duplicates were found.
3. `pass2()` for pathnames and directory validation.
4. `pass3()` for connectivity.
5. `pass4()` for reference counts and unreferenced objects.
6. `pass5()` for cylinder-group summaries and resource maps.

After phases it prints file/block/free-fragment summary, emits debug residue for missing files/blocks/duplicates/zero-link inodes, frees per-run structures, marks the superblock dirty when modified, writes duplicate superblocks for conversion mode, and calls `ckfini(resolved)` so unresolved answers or required reruns prevent marking the filesystem clean.

## Dependencies

- FFS/UFS metadata via `<ufs/ufs/dinode.h>` and `<ufs/ffs/fs.h>`.
- `fsck.h`, `extern.h`, and `fsutil.h` for phase APIs, block device handling, prompts, and buffer utilities.
- `setup.c` owns opening and validation; pass files own checks; `utilities.c` owns I/O finalization.

## Risks And Edge Cases

- `resolved` is deliberately cleared when a user refuses a fix or `rerun` is set; this prevents a dirty filesystem from being marked clean.
- Preen mode treats setup failure and duplicate blocks as fatal paths.
- Alternate superblock and conversion options disable clean-skip behavior.
- If the root filesystem is modified, the code attempts a read-only mount update/reload and otherwise requests reboot.
