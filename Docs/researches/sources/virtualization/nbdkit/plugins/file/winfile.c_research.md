# File Research: sources/virtualization/nbdkit/plugins/file/winfile.c

Windows implementation of the production nbdkit file plugin.

Key behavior:
- Supports only `file=<FILENAME>` / magic file parameter.
- Opens with `CreateFile`, requesting write access unless readonly; falls back to readonly on write-open failure.
- Detects Windows volume paths using `\\.\`.
- For volumes, obtains size with `IOCTL_DISK_GET_LENGTH_INFO` and sector size with `IOCTL_DISK_GET_DRIVE_GEOMETRY`.
- For regular files, obtains size with `GetFileSizeEx`.
- Detects sparse files with `GetFileInformationByHandle`.

Capabilities:
- Write support depends on open mode.
- Flush is advertised only for writable handles because Windows rejects flush on readonly handles.
- Trim and extents are advertised for sparse files.
- Zero is advertised generally.
- Block-size callback returns sector constraints for volumes and no constraints for regular files.
- Parallel thread model.

I/O behavior:
- Uses `ReadFile`/`WriteFile` with `OVERLAPPED` offsets for positional I/O.
- FUA on writes and trims/zeros calls `FlushFileBuffers`.
- Trim uses `FSCTL_SET_ZERO_DATA`.
- Zero uses `FSCTL_SET_ZERO_DATA`, but returns `ENOTSUP` for sparse files when `MAY_TRIM` is not set, allowing fallback to writing zeroes.
- Extents use `FSCTL_QUERY_ALLOCATED_RANGES`, adding hole extents between allocated ranges.

Error handling:
- Converts Windows error codes to strings via `FormatMessageA`.
- Gives a specific diagnostic for likely unaligned reads on 4K raw devices.
