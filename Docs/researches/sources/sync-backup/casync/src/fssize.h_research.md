# sources/sync-backup/casync/src/fssize.h

## Purpose

`fssize.h` declares the filesystem/image size detection helper.

## Important APIs, Types, and Functions

It exposes `read_file_system_size(int fd, uint64_t *ret)` and includes `<inttypes.h>` for `uint64_t`.

## Control Flow

Callers pass an open fd and interpret `1` as detected, `0` as unknown, and negative values as errors.

## State and Persistence Behavior

The API is read-only in the implementation and should not move the fd offset.

## Dependencies and Integration Points

It is a lightweight header for encoder or image handling code that wants to infer usable payload size from an image file rather than raw file length.

## Risks and Edge Cases

Consumers must not treat `0` as an error; it means no known filesystem signature. The helper is format-limited.

## Test Signals

Tests should assert return-value contract and fd-offset preservation through the implementation.
