# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ctf.c

## Purpose
Provides ELF linker-file support for loading Compact C Type Format (CTF) metadata for kernel modules, primarily for DDB CTF type lookup. This file is included by both `link_elf.c` and `link_elf_obj.c`.

## Main Elements
- `link_elf_ctf_get()`:
  - Validates arguments and initializes `linker_ctf_t`.
  - When `DDB_CTF` is enabled, returns cached CTF data if already loaded, remembers failed missing-section attempts with `ctfcnt == -1`, and refuses to load while panicking or in KDB.
  - Opens the module path, reads the ELF header and section headers, validates ELF shape, loads section-name strings, and searches for `.SUNW_ctf`.
  - Reads and validates the CTF header magic and supported versions 2 or 3.
  - Allocates the CTF buffer, handles compressed CTF via zlib `uncompress()`, preserves the CTF header, and stores pointers/counts in the ELF file structure.
  - Fills `linker_ctf_t` with CTF data, DDB symbol/string tables, symbol counts, and offset/length pointers.
  - Frees temporary buffers and closes the vnode on exit.
  - Returns `EOPNOTSUPP` when `DDB_CTF` is not compiled in.
- `link_elf_ctf_get_ddb()` returns already-loaded CTF data for debugger consumers or `ENOENT` if unavailable.
- `link_elf_ctf_lookup_typename()` retrieves loaded CTF and, when DDB is enabled, calls `db_ctf_lookup_typename()`.

## Dependencies And Integration
Depends on linker ELF private state, vnode I/O, ELF section metadata, `sys/ctf.h`, DDB CTF helpers, optional zlib, current thread credentials, and module pathnames.

## Risk Notes
The loader reads kernel module files directly and trusts validated ELF/CTF metadata to size allocations. It checks ELF header shape, section table presence, CTF magic, CTF version, and decompression status. Cached failure with `ctfcnt == -1` avoids repeated filesystem work for modules without CTF. CTF data is intentionally retained for later debugger use.
