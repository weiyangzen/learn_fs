# File Research: sources/local-fs/e2fsprogs/misc/e2fuzz.sh

## Purpose
Shell harness for repeatedly creating, corrupting, mounting, mutating, and repairing ext filesystem images with `e2fuzz` and `e2fsck`.

## Main Behaviors
- Creates a temporary mke2fs config under `/tmp/mke2fs.conf`.
- Builds a base image with configurable features, block size, inode size, image size, extended mke2fs options, and source data directory.
- Populates the image by mounting it and copying repeated copies of `SRCDIR`.
- For each pass:
  - Copies the base image.
  - Relabels it with `tune2fs`.
  - Corrupts it with `e2fuzz`.
  - Attempts a kernel loop mount or optional `fuse2fs` mount.
  - Runs filesystem operations: recursive listing, file reads, xattr listing, append writes, renames, copy/remove tree.
  - Runs `e2fsck -fy` up to `MAX_FSCK` times, detecting lack of progress by comparing logs.
  - Verifies the repaired image with `e2fsck -fn`.
  - Mounts the repaired image again and repeats read/write/remove checks.
  - Removes per-pass images/logs on success.

## Options
- `-b`: filesystem block size.
- `-B`: corruption bytes passed to `e2fuzz`.
- `-d`: working directory.
- `-E`: mke2fs extended options.
- `-F`: e2fsck extended options.
- `-f`: skip fsck after each pass.
- `-I`: inode size.
- `-n`: number of passes.
- `-O`: additional filesystem features.
- `-p`: use system tools instead of prepending local build dirs to `PATH`.
- `-s`: image size.
- `-S`: source directory.
- `-x`: maximum fsck passes.
- `-u`: use `fuse2fs` when available.

## Dependencies
- `mke2fs`, `e2fsck`, `tune2fs`, `e2fuzz`, `dumpe2fs`.
- Mount/umount, loop module, `truncate`, `cp`, `find`, `xargs`, `attr`, `dd`, `sync`, `stat`, `du`, `awk`, `diff`.
- Optional local `fuse2fs`.

## Notes and Edge Cases
- Defaults exercise many ext4 features including journal, extents, 64bit, metadata checksums, bigalloc, sparse_super2, and inline_data.
- The script treats out-of-memory and no-free-block fsck failures as environmental limits rather than fuzz failures.
- Uses shell pipelines with subshells in some loops; `break`/`exit` behavior is controlled by the pipeline/subshell context.
