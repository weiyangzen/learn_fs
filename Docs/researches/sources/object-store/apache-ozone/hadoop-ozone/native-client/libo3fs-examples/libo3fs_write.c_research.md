# sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs-examples/libo3fs_write.c

## Purpose

`libo3fs_write.c` is a native example program that writes patterned data to an Ozone `o3fs` file through the libo3fs wrapper.

## Important APIs and Functions

- `main(int argc, char **argv)` parses filename, total file size, buffer size, host, port, bucket, and volume.
- Uses `o3fsConnect`, `o3fsOpenFile`, `o3fsWrite`, `o3fsCloseFile`, and `o3fsDisconnect`.

## Control Flow

The program validates argument count after assigning variables from `argv`, connects to O3FS, checks parsed file size and buffer size constraints, casts buffer size to `tSize`, opens the output file write-only, allocates a buffer, fills it with repeated lowercase letters, loops until the requested file size is written in full or partial buffer chunks, validates each `o3fsWrite` return value, then frees, closes, disconnects, and exits.

## State and Persistence

It persists remote object data by writing the requested file. Local state is limited to handles, counters, and the heap buffer.

## Dependencies and Integration Points

It depends on `o3fs.h`, libhdfs-compatible type definitions, POSIX flags, and standard C library parsing/allocation. It is an example writer for native Ozone filesystem access.

## Risks and Edge Cases

The program reads `argv` before checking `argc`. It checks `errno == ERANGE` for file size without clearing `errno` before `strtoul` and stores the result in `off_t`, so overflow behavior is platform-sensitive. It uses `ULONG_MAX` without including `<errno.h>` in the source read, though `errno` is referenced. A zero buffer size would create an infinite write loop because `nrRemaining -= bufferSize` never advances. Error exits after failed writes do not free/close/disconnect.

## Test Signals

Smoke tests should write known sizes, including non-multiple buffer sizes, and then read back data. Negative tests should cover missing args, zero buffer, oversized buffer, parse overflow, failed connect, failed open, and short writes.
