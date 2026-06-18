# sources/user-network-fs/s3fs-fuse/test/cr_filename.cc

## Purpose
Helper program for testing object/file names containing a carriage return byte.

## Important APIs, Types, And Control Flow
`main` requires one base path argument, appends `\r` into a fixed buffer, creates the file with `open(O_CREAT|O_RDWR)`, closes it, verifies it with `stat`, and removes it with `unlink`.

## State And Persistence
Creates and deletes one filesystem object whose name ends in CR. It leaves no intended persistent state after success.

## Dependencies And Integration Points
Depends on POSIX `open`, `close`, `stat`, and `unlink`. Called by `integration-test-main.sh` in `test_cr_filename`, indirectly testing `string_util.cpp` CR encoding for S3 XML list parsing.

## Risks And Test Signals
Uses a 4096-byte fixed buffer and truncates silently if the base path is too long. It does not inspect contents or listing, only create/stat/delete. Success under the mounted filesystem is a direct signal that CR-named objects survive round trips.
