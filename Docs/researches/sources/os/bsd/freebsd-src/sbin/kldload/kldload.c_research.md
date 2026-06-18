# File Research: sources/os/bsd/freebsd-src/sbin/kldload/kldload.c

## Purpose
Implements `kldload`, the command-line utility for loading kernel linker modules.

## Main Responsibilities
- Loads one or more kernel modules using `kldload()`.
- Supports quiet, verbose, and already-loaded tolerant behavior.
- Warns when a bare `.ko` filename in the current directory may be shadowed by a module found in `kern.module_path`.

## Key Implementation Details
- `path_check()`:
  - Ignores names containing `/`.
  - Only checks names containing `.ko`.
  - Compares current-directory file `st_dev/st_ino` against files found through `kern.module_path`.
  - Warns if the module path version differs from the current directory file.
- Main loop attempts each module independently and accumulates errors.
- `-n` treats `EEXIST` as success.
- `-v` prints loaded module ID or already-loaded notice.
- `-q` suppresses warnings.

## Kernel/Userland Interface
- Reads `kern.module_path` through `sysctlnametomib()` and `sysctl()`.
- Loads modules with `kldload()`.

## Notable Edge Cases
- `ENOEXEC` prints a dmesg-oriented diagnostic instead of only `warn()`.
- If `path_check()` cannot find the bare `.ko` in module path, loading is skipped and counted as an error.
