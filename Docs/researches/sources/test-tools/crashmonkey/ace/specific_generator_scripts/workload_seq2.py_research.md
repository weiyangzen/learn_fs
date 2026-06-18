# sources/test-tools/crashmonkey/ace/specific_generator_scripts/workload_seq2.py

## Purpose

`workload_seq2.py` is the second C++ workload translator for ACE j-lang. It retains most of `workload_seq1.py` but adjusts generated code for later sequence workloads: checkpoint return values are taken from the j-lang line, rename goes through `cm_->CmRename`, direct write goes through `cm_->CmOpen`, `rmdir` is supported, and generated output no longer appends `output_name` to the j-lang-derived filename.

## Important APIs, Types, and Functions

- CLI arguments mirror `workload_seq1.py`.
- Insertion-map helpers and `insertDefine`/`insertDeclare` are shared in purpose with seq1.
- Operation emitters cover fallocate, mkdir, open file/dir, mknod, remove/unlink, truncate, close, rmdir, fsync/fdatasync, sync, link/symlink, checkpoint, rename, xattr, write, direct write, mmap write, and no-op `none`.
- `insertCheckpoint` emits `return <line argument>` when the local checkpoint equals the requested checkpoint.
- `insertRename` emits `cm_->CmRename` rather than raw `rename`.
- `insertWrite` differentiates buffered `WriteData`, direct `pwrite` through an O_DIRECT/O_SYNC `cm_->CmOpen`, and mmap-based writes with offset-aware mapping/msync.
- `insertFunctions` is the central dispatcher.

## Control Flow

`main` validates input, creates the target directory, resolves the base file inside that target directory, scans anchor lines, copies the base file to `target_path + test_file + ".cpp"`, and processes the j-lang file. The j-lang `#` markers select the insertion area and each operation line is translated into C++ text inserted at the tracked anchor offset.

## State and Persistence Behavior

The translator persists one generated C++ file and mutates it in place for every inserted operation. `redeclare_map` prevents duplicate declarations for file descriptors, mmap pointers, and direct-write buffers. Checkpoint state is generated into the C++ runtime as `local_checkpoint`, and the return value at a checkpoint is controlled by the j-lang argument.

## Dependencies and Integration Points

This script is integrated with sequence generators such as `seq3nestedgenerator.py`, which shells out to `workload_seq2.py`. Generated C++ relies on CrashMonkey wrappers for open/close/fsync/fdatasync/sync/checkpoint/rename/mmap/msync/munmap, and on POSIX/Linux syscalls for fallocate, mkdir, mknod, truncate, xattr, direct I/O, and pwrite. It expects a `base.cpp` already staged under the target path.

## Risks and Edge Cases

- Python 2 only.
- `operation_map` is created but unused, indicating drift from an older permutation generator.
- Path flattening can collide.
- Insertion offsets are brittle and depend on exact snippet line counts.
- `insertMknodFile` still models `mknod` as a file descriptor.
- Direct and mmap generated code has fixed text buffers and manual close/unmap behavior; repeated writes to the same file can depend heavily on `redeclare_map` side effects.
- Output naming as `target_path + test_file + ".cpp"` can produce surprising nested/duplicated paths when `test_file` includes directories.

## Test Signals

Validation should include generator-to-translator smoke tests from `seq3nestedgenerator.py`, compilation of generated C++ tests, and runtime crash tests that verify `cm_->CmRename`, checkpoint return values, `rmdir`, direct write, and mmap paths are observed by CrashMonkey. A regression fixture comparing seq1 and seq2 output for the same j-lang can make intentional behavior differences explicit.
