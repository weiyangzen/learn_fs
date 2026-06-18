# File Research: sources/os/bsd/freebsd-src/sbin/kldstat/kldstat.c

## Purpose
Implements `kldstat`, which lists loaded kernel linker files and modules.

## Main Responsibilities
- Lists all loaded KLD files or a selected file by ID/name.
- Finds and displays a module by module name.
- Supports verbose module listing under each file.
- Supports humanized size output.
- Optionally displays module data fields.

## Key Implementation Details
- `printfile()` uses `kldstat()` to fetch `struct kld_file_stat`, then prints ID, refs, address, size, and name.
- Verbose mode prints pathname and contained modules via `kldfirstmod()`/`modfnext()`.
- `printmod()` fetches `struct module_stat` using `modstat()`.
- `-m` uses `modfind()`.
- `-n` uses `kldfind()`.
- Quiet mode returns success/failure without printing when searching.

## Kernel/Userland Interface
Uses:
- `kldnext()`
- `kldstat()`
- `kldfind()`
- `kldfirstmod()`
- `modfnext()`
- `modfind()`
- `modstat()`

## Output Behavior
- Default columns: ID, refs, address, size, name.
- `-h` uses `humanize_number()`.
- `-d` adds module data tuple printing.
