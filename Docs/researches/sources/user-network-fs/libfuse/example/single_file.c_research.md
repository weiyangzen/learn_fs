# sources/user-network-fs/libfuse/example/single_file.c

## Purpose
`single_file.c` is shared implementation code for examples that expose one regular file backed by another file or block device. It supports both low-level and high-level FUSE operation handlers, common option parsing, metadata synthesis, statfs/statx, bounded reads/writes, timestamp updates, and service-mediated opening of backing resources.

## Important APIs, Types, and Functions
The global `struct single_file single_file` stores the backing fd, logical size, block count, mode, read-only/direct-IO/sync/block-device flags, blocksize, timestamps, and mutex. `SINGLE_FILE_INO` is `FUSE_ROOT_ID + 1`; `single_file_name` defaults to `single_file`. Important helpers include path/ino mapping functions, `dirbuf_add()`, `reply_buf_limited()`, `sf_stat()`, optional `sf_statx()`, `single_file_statfs()`, low-level handlers (`single_file_ll_*`), high-level handlers (`single_file_hl_*`), option functions, `single_file_service_open()`, I/O bounds checks, `single_file_pread/pwrite()`, `single_file_configure()`, and `single_file_close()`.

## Control Flow
Service examples parse options through `single_file_opt_proc()`, request/open a backing resource with `single_file_service_open()`, then call `single_file_configure()`. Configure stats the backing fd, derives block size and size from file or block-device ioctls, validates user-provided size/blocksize constraints, rounds size down to blocksize, computes block count, and initializes timestamps/name/mode. FUSE operations map root and single-file paths to fixed inode numbers, synthesize directory entries, reply with metadata, enforce read-only policy on open and metadata changes, clamp reads/writes to logical size, and call pread/pwrite loops on the backing fd.

## State and Persistence
The backing file/device contains persistent data. Metadata such as exposed name, mode bits, timestamps, read-only state, and logical size are process-local and reset on restart unless derived from the backing resource. `single_file_pwrite()` optionally `fsync`s when `sync` is set and updates mtime/ctime under the mutex. Attribute and entry timeouts are zero, favoring fresh metadata.

## Dependencies and Integration Points
The file includes both `fuse_lowlevel.h` and `fuse.h`, plus `fuse_service.h`. Linux block device integration uses `BLKSSZGET`, `BLKGETSIZE64`, and optional `statx` direct-I/O alignment fields. It is directly integrated by `service_hl.c` and `service_ll.c`, with compile-time macros enabling prototype visibility in `single_file.h`.

## Risks
`single_file_check_write()` compares and adjusts `size_t` counts against signed `isize`; invalid negative positions are not explicitly handled and rely on FUSE/kernel call patterns. `single_file_service_open()` retries read-only after permission failures and mutates `single_file.ro`; callers must expect downgrade. The code exposes immutable statx attributes for read-only mode but does not persist chmod/utimens to the backing file. `single_file_close()` closes `backing_fd` without checking whether it is valid.

## Test Signals
Unit-style tests should cover `parse_num_blocks()` suffixes, blocksize/size validation, read/write clamping at EOF, read-only write rejection, sync write fsync failures, stat/statx/statfs values, custom exposed filename, high-level and low-level directory listing, and service-open fallback from read-write to read-only. Integration tests should compare bytes in the exposed file against the backing file.
