# File Research: sources/os/linux/linux/fs/binfmt_elf.c

## Purpose
Main Linux ELF executable loader and ELF core dumper. It registers the standard ELF binary format, validates ELF images, maps executable/interpreter segments, builds the initial user stack and aux vector, starts execution, and emits ELF core files under `CONFIG_ELF_CORE`.

## Loader Registration
- `elf_format` provides:
  - `load_binary = load_elf_binary`
  - `core_dump = elf_core_dump` when coredumps are enabled
  - `min_coredump = ELF_EXEC_PAGESIZE`
- Registered with `core_initcall(init_elf_binfmt)` and removed at module exit.

## Stack and Aux Vector
- `create_elf_tables()`:
  - aligns stack
  - copies platform/base-platform strings if provided
  - generates `AT_RANDOM`
  - fills `mm->saved_auxv`
  - emits hardware capability, page size, clock tick, program header info, base, flags, entry, credentials, secureexec, execfn, execfd, rseq, and platform aux entries
  - lays out `argc`, argv pointers, envp pointers, and auxv on the new user stack
  - updates `arg_start/end` and `env_start/end`

## Segment Mapping
- `padzero()`: clears trailing partial page after file-backed segment contents.
- `elf_map()`: maps file-backed segment bytes, using `total_size` for first mapping to reserve the full image and then unmap holes.
- `elf_load()`: maps file data and zeroes/maps bss-like memory through `vm_brk_flags()`.
- `total_mapping_size()`: computes contiguous PT_LOAD span.
- `maximum_alignment()`: computes maximum power-of-two PT_LOAD alignment.

## ELF Validation and Program Header Loading
- `elf_read()` wraps exact-size `kernel_read()`.
- `load_elf_phdrs()` validates program header entry size/count/total size and reads headers.
- Architecture hooks:
  - `arch_elf_pt_proc()`
  - `arch_check_elf()`
  - `arch_elf_adjust_prot()` through `make_prot()`
- GNU property parsing:
  - `parse_elf_properties()`
  - `parse_elf_property()`

## Main Exec Flow
`load_elf_binary()`:
1. Validates ELF magic, type, architecture, non-FDPIC, and mmap capability.
2. Loads program headers.
3. Handles `PT_INTERP`: reads interpreter path, opens interpreter, applies `would_dump()`, and reads interpreter ELF header.
4. Processes `PT_GNU_STACK`, processor-specific headers, interpreter headers, and GNU properties.
5. Allows architecture final rejection through `arch_check_elf()`.
6. Calls `begin_new_exec()`, sets personality, applies `READ_IMPLIES_EXEC`, snapshots ASLR state, and calls `setup_new_exec()`.
7. Sets up argument pages.
8. Maps every PT_LOAD segment with correct protections and ET_EXEC/ET_DYN placement rules.
9. Handles PIE/static-PIE load bias, alignment, interpreter mapping, and brk placement/randomization.
10. Creates ELF tables, sets mm code/data/stack bounds, optionally maps page zero for SVr4 compatibility, applies platform register initialization, finalizes exec, and starts the thread.

## Core Dump Support
Under `CONFIG_ELF_CORE`, the file implements:
- ELF note helpers (`memelfnote`, `notesize`, `writenote`)
- ELF/core/program-header construction helpers
- process and thread notes:
  - `NT_PRSTATUS`
  - `NT_PRPSINFO`
  - `NT_SIGINFO`
  - `NT_AUXV`
  - `NT_FILE`
  - regset-backed notes
- `fill_files_note()` records mapped files for debuggers.
- `elf_core_dump()` writes ELF header, note phdr, PT_LOAD phdrs for VMAs, arch extra phdr/data, notes, VMA memory ranges, and extended numbering section header when needed.

## Security and Robustness Notes
- Validates interpreter path size and NUL termination.
- Uses `MAP_FIXED_NOREPLACE` for collision-sensitive executable mappings.
- Checks `p_filesz <= p_memsz`, task-size overflow, and mmap capability.
- Preserves `would_dump()` behavior for unreadable binaries with interpreters.
- GNU property parsing enforces sorted unique property types.
