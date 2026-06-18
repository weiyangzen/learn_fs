# File Research: sources/os/bsd/freebsd-src/sbin/kldunload/kldunload.c

## Purpose
Implements `kldunload`, the command-line utility for unloading kernel linker files.

## Main Responsibilities
- Unloads modules by file ID or by name.
- Supports forced unload.
- Supports verbose display before unloading.

## Key Implementation Details
- `-i` treats arguments as numeric file IDs.
- Without `-i`, arguments are resolved with `kldfind()`.
- `-f` selects `LINKER_UNLOAD_FORCE`; otherwise uses `LINKER_UNLOAD_NORMAL`.
- `-v` fetches `kld_file_stat` and prints module name and ID before unloading.
- `-n` is accepted as a backward-compatible no-op.

## Kernel/Userland Interface
Uses:
- `kldfind()`
- `kldstat()`
- `kldunloadf()`

## Notable Edge Cases
- ID parsing uses `atoi()` and checks only for negative values, so non-numeric strings become `0`.
- The error message for invalid ID references `optarg` even though the failing string is held in `filename`.
