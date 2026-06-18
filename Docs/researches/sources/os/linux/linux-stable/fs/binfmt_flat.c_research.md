# File Research: sources/os/linux/linux-stable/fs/binfmt_flat.c

This file implements the `bFLT` flat binary loader, mainly for embedded/no-MMU systems, with optional compressed flat support.

Loader registration:
- `flat_format` registers `load_flat_binary()`.
- Registered at core init.

Stack setup:
- `create_flat_tables()` builds argc, optional argv/envp pointers-on-stack, argv pointer array, envp pointer array, and records `mm->arg_*` and `mm->env_*`.

Compressed support:
- Under `CONFIG_BINFMT_ZFLAT`, `decompress_exec()` parses a gzip header, rejects unsupported flags, initializes zlib inflate, streams file contents through a small buffer, and writes decompressed bytes to the target.

Relocation:
- `calc_reloc()` converts flat-file relative offsets into loaded text/data addresses and kills the process with SIGSEGV on invalid relocation.
- `old_reloc()` supports legacy flat relocation format when `CONFIG_BINFMT_FLAT_OLD` is enabled.
- `skip_got_header()` skips RISC-V GOT PLT reserved header entries.
- Relocation handling supports GOTPIC relocations and relocation table entries, using arch hooks `flat_get_relocate_addr()`, `flat_get_addr_from_rp()`, and `flat_put_addr_at_rp()`.

Main load flow:
- `load_flat_file()` validates the `bFLT` header, version, flags, size sanity, zflat availability, and `RLIMIT_DATA`.
- Calls `begin_new_exec()`, sets `PER_LINUX_32BIT`, and `setup_new_exec()`.
- Computes extra memory for BSS/stack/relocs.
- Handles no-MMU ROM text plus RAM data mapping when possible.
- Otherwise maps/copies text and data together into RAM, supporting gzip whole-file or gzip-data modes.
- Sets `mm->start_code`, `end_code`, `start_data`, `end_data`, `start_brk`, and `brk`.
- Stores loaded module metadata in `lib_info`.
- Applies GOT and relocation-table fixups.
- Flushes user icache and clears BSS, brk slack, and stack area.

Top-level binary load:
- `load_flat_binary()` computes extra stack needs from argc/envp and argument pages, loads the flat file, updates shared-library data segment pointers when configured, sets binfmt, creates argument pages/tables for MMU or no-MMU, applies `FLAT_PLAT_INIT`, finalizes exec, and starts the thread at the flat entry point.

Integration:
- Uses Linux binfmt, mm/mmap, read_code, user-copy, zlib, arch flat hooks, and task register setup.
- Supports a limited `MAX_SHARED_LIBS` structure, currently one shared library slot in this configuration.

Risk notes:
- This parser is highly sensitive to header arithmetic; it rejects sizes with high bits set and enforces data+bss rlimit.
- `calc_reloc()` sends SIGSEGV on invalid relocation in addition to returning failure.
- Optional gzip paths use kernel buffers/vmalloc on MMU for simpler user copying.
- The no-MMU memory layout manually tracks brk/stack boundaries through `mm->context.end_brk`.
