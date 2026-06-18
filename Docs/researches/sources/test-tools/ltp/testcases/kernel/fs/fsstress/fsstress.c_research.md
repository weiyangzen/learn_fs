# sources/test-tools/ltp/testcases/kernel/fs/fsstress/fsstress.c

## Purpose

`fsstress.c` is a randomized metadata and data operation generator for filesystems. It creates per-process subtrees and repeatedly performs weighted operations such as create, mkdir, mknod, link, symlink, rename, unlink, rmdir, stat, read, write, direct read/write, fsync, fdatasync, sync, truncate, getdents, chown, and optional XFS allocation, attribute, bulkstat, reservation, and error-injection calls.

## Important APIs, Types, and Functions

Core types include `opdesc_t`, `fent_t`, `flist_t`, and `pathname_t`. `ops[]` maps operation IDs to names, function pointers, default frequencies, write/read classification, and XFS-only status. File state is tracked in `flist[FT_nft]` with file-type tags for directories, regular files, symlinks, devices, and realtime files. Important infrastructure functions include `make_freq_table`, `process_freq`, `doproc`, `get_fname`, `generate_fname`, `fent_to_name`, `add_to_flist`, `del_from_flist`, `fix_parent`, `namerandpad`, and the `*_path` wrappers that retry after `ENAMETOOLONG` by walking directories.

## Control Flow

`main` parses options for directory, operation counts, processes, loops, seed, operation frequencies, random name padding, cleanup, and XFS controls. It builds the weighted frequency table, creates or enters the target directory, probes maximum file size, initializes directory cache, selects a seed, optionally configures XFS geometry/error injection, and runs `doproc` directly or in child processes. `doproc` creates a `p<procid>` directory, seeds the random generator, and dispatches `operations` random functions from `ops[]`.

## State and Persistence Behavior

Runtime state is mostly in globals: `flist`, `dcache`, `nameseq`, `seed`, `maxfsize`, `procid`, `homedir`, `freq_table`, and XFS geometry/error fields. The filesystem state is intentionally persistent during an iteration and is removed by `rm -rf <dir>/*` unless `-c` requests no cleanup. In-memory file lists are reset after cleanup.

## Dependencies and Integration Points

The default LTP build defines `NO_XFS`, so `xfscompat.h` supplies `MAXNAMELEN`, `struct dioattr`, `MIN`, and `MAX`, and XFS-specific operations are disabled. Without `NO_XFS`, the file integrates with libxfs, attr APIs, XFS ioctls, realtime geometry, and error injection. It also uses large-file syscalls, `O_DIRECT`, `posix_memalign`, process groups, optional `prctl(PR_SET_PDEATHSIG)`, and LTP `ARRAY_SIZE`.

## Risks and Edge Cases

This is a stress generator, not a model checker: many operation errors are logged only in verbose mode and are not fatal. Global file lists are per process, so concurrent children do not share a consistent model of each other's mutations. The XFS forced-shutdown check compares `stat64()` return value to `EIO` instead of checking `errno`. Recursive path wrappers mutate cwd and depend on `check_cwd` only in debug builds. The default non-XFS build disables substantial legacy coverage.

## Test Signals

Pass is survival: exit status zero after all loops and child waits. Useful diagnostics are printed seed, verbose operation traces, unexpected child death, direct-I/O setup failures, and filesystem/kernel errors surfaced as process failures. Reproducibility depends on saving the printed seed and options.
