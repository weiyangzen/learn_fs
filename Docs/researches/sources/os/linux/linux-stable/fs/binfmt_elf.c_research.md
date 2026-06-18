# File Research: sources/os/linux/linux-stable/fs/binfmt_elf.c

This file implements the standard ELF binary loader and ELF core dumper.

Loader registration:
- `elf_format` registers `load_elf_binary()` and, when enabled, `elf_core_dump()`.
- Registered at `core_initcall(init_elf_binfmt)`.

ELF exec setup:
- `load_elf_binary()` validates ELF magic/type/architecture, rejects FDPIC, loads program headers, handles `PT_INTERP`, reads interpreter headers, processes `PT_GNU_STACK`, architecture processor headers, GNU properties, and architecture final checks.
- Calls `begin_new_exec()`, sets personality, applies `READ_IMPLIES_EXEC`, snapshots ASLR state, calls `setup_new_exec()`, and maps the user stack with `setup_arg_pages()`.
- Maps `PT_LOAD` segments with `elf_load()`, handling ET_EXEC fixed mapping, ET_DYN PIE/randomized mapping, static PIE loader behavior, alignment, first-load total reservation, BSS zeroing, and overflow checks.
- Loads an interpreter through `load_elf_interp()` when `PT_INTERP` is present.
- Creates the initial stack and auxiliary vector through `create_elf_tables()`.
- Sets `mm` code/data/brk/stack fields, randomizes brk when configured, optionally maps page zero for SVr4 compatibility, applies `ELF_PLAT_INIT`, finalizes exec, and starts the thread.

Support functions:
- `padzero()` clears trailing bytes after file-backed segment data.
- `elf_map()` wraps `vm_mmap()` and unmaps holes after the first full-image reservation.
- `elf_load()` maps file bytes and creates anonymous BSS pages.
- `total_mapping_size()` and `maximum_alignment()` support safe ET_DYN layout.
- `load_elf_phdrs()` reads and validates program headers.
- `parse_elf_properties()` and `parse_elf_property()` read `PT_GNU_PROPERTY` notes and pass properties to architecture code.

Core dump:
- Builds ELF headers, note headers, process notes, per-thread register/regset notes, auxv, siginfo, and NT_FILE mapped-file notes.
- Supports extended program header numbering with `PN_XNUM`.
- Emits PT_LOAD program headers for VMA dumps and writes VMA contents with `dump_user_range()`.
- Supports architecture extra notes/data hooks.

Integration:
- Central to Linux `execve()` for normal ELF binaries.
- Uses mm, binfmt, security, randomization, coredump, regset, rseq, arch ELF hooks, file mapping, and user-copy APIs.

Risk notes:
- This is security-critical parsing and mapping code; it has extensive bounds checks for program-header size, segment overflow, interpreter paths, GNU property ordering, and task address limits.
- The loader carefully distinguishes ET_DYN with interpreter from static PIE to avoid loader/program collisions.
- Core dump NT_FILE generation dynamically resizes to handle long paths and obeys `core_file_note_size_limit`.
