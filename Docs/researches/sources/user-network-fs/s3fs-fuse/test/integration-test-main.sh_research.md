# sources/user-network-fs/s3fs-fuse/test/integration-test-main.sh

## Purpose
Main integration test suite for mounted s3fs behavior. It exercises POSIX-like file operations, S3 metadata mapping, multipart/cache behavior, implicit directory handling, xattrs/ACLs, concurrent access, sparse writes, statvfs, and selected pjdfstest cases.

## Important APIs, Types, And Control Flow
The script sources `test-utils.sh`, defines many `test_*` functions, calls `init_suite`, registers tests in `add_all_tests`, and runs them with `run_suite`. Tests cover create/append/truncate/shrink/read, rename of files/directories, shell redirects, mkdir/rmdir, chmod/chown, listing, non-empty rmdir errors, external S3 object creation/modification, metadata updates for small/large objects, rename before close, multipart upload/copy/mix, special characters, hardlink rejection, mknod, symlink, xattrs, timestamp update semantics, parent directory time updates, POSIX ACLs, recursive removal, copy/seek/overwrite, concurrent reads/writes/directory updates, second-fd reads, multioffset writes, content type, cache-stat files, zero-byte cache stats, sparse uploads, mixed upload entities, ensure-diskfree behavior, implicit directories, CR filenames, skipped writes, non-boundary writes, mountpoint time/statvfs, and pjdfstest subsets. `add_all_tests` selects tests based on mount options, OS, cache/ensure-diskfree settings, Alpine, Ubuntu version, and macOS FUSE-T caveats.

## State And Persistence
Creates and removes many files under the mounted bucket, `/tmp`, and cache directories. It mutates S3 objects through `s3_cp`, local cache/stat files, xattrs, ACLs, metadata timestamps, and mounted directory structures. Some tests intentionally delete cache files to force remote re-fetch.

## Dependencies And Integration Points
Depends heavily on `test-utils.sh`, helper binaries (`junk_data`, `write_multiblock`, `mknod_test`, `truncate_read_file`, `cr_filename`), AWS/S3 helper functions, GNU/coreutils behavior, xattr/ACL tools, pjdfstest, S3Proxy or a real S3 endpoint, and mounted s3fs options from `small-integration-test.sh`.

## Risks And Test Signals
The suite is environment-sensitive: macOS FUSE-T, Alpine, Ubuntu 25.10, noatime/relatime, root privileges, ACL/xattr tool availability, cache options, and disk space all affect coverage. It can consume significant disk and network resources. Strong signals include all registered tests passing under both default `sigv4` and `ALL_TESTS` option matrices, plus sanitizer/Valgrind wrapper scripts.
