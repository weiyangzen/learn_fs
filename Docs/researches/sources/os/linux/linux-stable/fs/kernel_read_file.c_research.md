# File Research: sources/os/linux/linux-stable/fs/kernel_read_file.c

## Purpose

Provides generic helpers for reading a regular file into a kernel buffer, with Linux Security Module hooks before and after reading. Used by kernel subsystems that need to load firmware, policies, certificates, or other file-backed blobs.

## Main Function

`kernel_read_file()` validates partial-read rules, requires a regular file, denies concurrent write access with `deny_write_access()`, checks file size bounds, asks LSMs through `security_kernel_read_file()`, allocates a `vmalloc()` buffer if needed, reads with `kernel_read()` until the requested buffer is filled or EOF, and calls `security_kernel_post_read_file()` for whole-file reads.

## Wrapper APIs

- `kernel_read_file_from_path()` opens a path from the caller's namespace and reads it.
- `kernel_read_file_from_path_initns()` opens relative to the init task root.
- `kernel_read_file_from_fd()` validates an fd has `FMODE_READ` and reads from it.

## Error And Lifetime Notes

The function rejects empty/nonpositive files, files larger than `SSIZE_MAX`, whole-file reads whose buffer is too small, and invalid offset/buffer combinations. On error after internal allocation, it frees the buffer and nulls the caller pointer. `allow_write_access()` is always called before return after a successful deny.
