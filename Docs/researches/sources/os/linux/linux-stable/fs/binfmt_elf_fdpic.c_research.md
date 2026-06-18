# File Research: sources/os/linux/linux-stable/fs/binfmt_elf_fdpic.c

This file implements the ELF-FDPIC binary loader and FDPIC core dumper. FDPIC supports position-independent executables with explicit load maps, commonly for embedded/no-MMU architectures.

Loader registration:
- `elf_fdpic_format` registers `load_elf_fdpic_binary()` and optional `elf_fdpic_core_dump()`.
- Registered at core init and unregistered on module exit.

Exec flow:
- `is_elf()` validates ELF magic, type, architecture, and mmap capability.
- `elf_fdpic_fetch_phdrs()` reads program headers, validates header size/count, and extracts GNU stack policy/stack size.
- `load_elf_fdpic_binary()` validates executable and optional interpreter, loads both program-header tables, derives const-displacement flags, chooses stack executability, calls `begin_new_exec()`, sets personality including `PER_LINUX_FDPIC`, sets up the mm layout, maps executable/interpreter with `elf_fdpic_map_file()`, creates stack/auxv/loadmap tables, applies `ELF_FDPIC_PLAT_INIT`, finalizes exec, and starts the thread at interpreter or executable entry.
- On MMU systems, layout is delegated to `elf_fdpic_arch_lay_out_mm()` and `setup_arg_pages()`.
- On no-MMU systems, it manually maps a stack area and sets `context.end_brk`.

Load mapping:
- `elf_fdpic_map_file()` allocates an `elf_fdpic_loadmap`, maps all `PT_LOAD` segments according to arrangement flags, determines entry address, program-header address, and dynamic section address, validates that the dynamic section ends in a NULL entry, and merges adjacent loadmap segments on MMU.
- `elf_fdpic_map_file_constdisp_on_uclinux()` handles no-MMU constant-displacement loads by allocating one contiguous anonymous block, reading code into it, and clearing BSS.
- `elf_fdpic_map_file_by_direct_mmap()` maps individual load segments, handles independent/honour-vaddr/constdisp/contiguous arrangements, clears leading/trailing bytes, maps anonymous excess on MMU, and updates `mm` code/data bounds.

Stack and auxv:
- `create_elf_fdpic_tables()` copies platform strings, writes executable/interpreter load maps to user stack, creates auxv entries including `AT_BASE`, `AT_ENTRY`, credentials, secureexec, execfn, optional hwcap values, then builds argc/argv/envp tables.

Core dump:
- Adds FDPIC loadmap addresses into `elf_prstatus_fdpic`.
- Emits PRSTATUS/PRFPREG, PRPSINFO, AUXV, PT_LOAD headers, extra core phdrs/data, VMA dumps, and extended numbering metadata.

Integration:
- Uses ELF-FDPIC arch hooks, normal binfmt/exec/mm APIs, coredump APIs, regsets, and no-MMU conditional paths.
- Complements `binfmt_elf.c`; standard ELF handles non-FDPIC on MMU, while this file handles FDPIC and selected no-MMU ET_DYN cases.

Risk notes:
- Mapping correctness depends heavily on arch-provided FDPIC flags and layout hooks.
- Dynamic-section validation catches malformed FDPIC dynamic arrays, but broader segment overlap/arrangement validation is distributed across mapping and arch logic.
- Core dump format carries FDPIC-specific load maps so debuggers can relocate symbols.
