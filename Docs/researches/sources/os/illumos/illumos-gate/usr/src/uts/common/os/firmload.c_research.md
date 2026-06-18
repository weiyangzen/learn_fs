# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/firmload.c

## Purpose

`firmload.c` provides a small firmware-loading API for device drivers. It is derived from NetBSD’s firmload interface and adapted to illumos kernel object loading primitives.

## Data Model

`struct firmware_handle` contains:

- `fh_buf`: a `struct _buf *` returned by `kobj_open_path()`.
- `fh_size`: cached firmware file size.

Handles are allocated and freed with small wrappers around `kmem_alloc()` and `kmem_free()`.

## API Functions

`firmware_open()` validates `drvname`, `imgname`, and output handle pointer. It constructs `firmware/<drvname>/<imgname>` with `kmem_asprintf()`, allocates a handle, opens the image with `kobj_open_path(path, 1, 0)`, frees the path string, and maps open failure to `ENOENT`. It then retrieves file size with `kobj_get_filesize()`; on failure it closes the file and frees the handle. On success it stores the handle in `*fhp`.

`firmware_close()` closes the kobj file and frees the handle when non-NULL. It always returns 0.

`firmware_get_size()` asserts a non-NULL handle and returns the cached size.

`firmware_read()` asserts a non-NULL handle and reads `len` bytes from `offset` into `buf` via `kobj_read_file()`. It returns `0` on success and `-1` on read failure, matching the underlying kobj convention rather than errno-style reporting.

## External Interactions

The implementation depends on the kernel runtime linker/object APIs:

- `kobj_open_path()`
- `kobj_get_filesize()`
- `kobj_read_file()`
- `kobj_close_file()`

It also uses kernel allocation helpers and string allocation/freeing.

## Research Notes

This is intentionally minimal: it does no path normalization beyond fixed `firmware/<driver>/<image>` construction, caches only size and open buffer, and leaves firmware interpretation to callers. The main cleanup invariant is that every successful `kobj_open_path()` is closed by `firmware_close()` or the error path after failed size lookup.
