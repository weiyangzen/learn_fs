# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/asynch.h

## Purpose

`asynch.h` declares the older Solaris asynchronous I/O user interfaces.

## Interfaces

It defines `AIO_INPROGRESS` as the sentinel result value and declares:

- `aioread()`
- `aiowrite()`
- `aiocancel()`
- `aiowait()`

Large-file build logic remaps `aioread`/`aiowrite` to 64-bit variants under `_FILE_OFFSET_BITS=64`, and remaps 64-bit names back to native names on LP64 with `_LARGEFILE64_SOURCE`. Transitional `aioread64()` and `aiowrite64()` declarations are provided when applicable.

`MAXASYNCHIO` is set to 200 outstanding I/Os.

## Research Notes

This is a compatibility ABI header for pre-POSIX Solaris AIO. It shares `aio_result_t` with `aio.h` and remains relevant where old applications use `aioread`/`aiowrite`.
