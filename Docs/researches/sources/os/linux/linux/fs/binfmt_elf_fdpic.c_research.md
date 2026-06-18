# File Research: sources/os/linux/linux/fs/binfmt_elf_fdpic.c

## Purpose
Implements the ELF-FDPIC binary format loader and FDPIC core dumper. FDPIC supports position-independent executables with explicit load maps, especially for NOMMU and embedded architectures.

## Registration
- `elf_fdpic_format` provides:
  - `load_binary = load_elf_fdpic_binary`
  - `core_dump = elf_fdpic_core_dump` under `CONFIG_ELF_CORE`
- Registered with `core_initcall(init_elf_fdpic_binfmt)`.

## ELF Identification
- `is_elf()` checks ELF magic, type `ET_EXEC`/`ET_DYN`, architecture, and mmap capability.
- `elf_check_fdpic()` determines FDPIC support; non-FDPIC ELF is delegated to standard `binfmt_elf` on MMU systems.
- `is_constdisp()` determines whether constant displacement mapping should be used.

## Program Header Handling
- `elf_fdpic_fetch_phdrs()` validates header entry size/count, reads headers, and extracts `PT_GNU_STACK` stack permissions and requested stack size.

## Main Exec Flow
`load_elf_fdpic_binary()`:
1. Initializes executable and interpreter parameter structures.
2. Validates executable and FDPIC constraints.
3. Reads executable program headers.
4. Scans for `PT_INTERP`, opens interpreter, applies `would_dump()`, and reads interpreter header.
5. Reads interpreter program headers when present.
6. Determines stack size and executable-stack policy.
7. Calls `begin_new_exec()`, sets personality including `PER_LINUX_FDPIC`, applies `READ_IMPLIES_EXEC`, and sets up new exec state.
8. Lays out stack/brk for MMU or NOMMU.
9. Maps executable and interpreter with `elf_fdpic_map_file()`.
10. Creates user stack tables and load maps with `create_elf_fdpic_tables()`.
11. Applies architecture platform initialization, finalizes exec, and starts the thread at interpreter or executable entry.

## User Stack and Load Maps
- `create_elf_fdpic_tables()`:
  - copies platform/base-platform strings
  - copies executable and interpreter load maps onto user stack
  - records load map addresses in `mm->context`
  - builds aux vector including `AT_BASE`, `AT_ENTRY`, credentials, secureexec, execfn, execfd, and platform entries
  - lays out argc/argv/envp and updates mm argument/environment bounds

## Mapping Logic
- `elf_fdpic_map_file()`:
  - counts PT_LOAD segments
  - allocates flexible load map
  - dispatches to constant-displacement mapping on NOMMU or direct mmap
  - resolves entry point, program header address, and dynamic section address
  - validates dynamic section has aligned entries and final NULL tag
  - merges adjacent load map segments on MMU where possible
- `elf_fdpic_map_file_constdisp_on_uclinux()`:
  - NOMMU constant-displacement loader using one anonymous allocation and `read_code()`
- `elf_fdpic_map_file_by_direct_mmap()`:
  - maps PT_LOAD segments independently, honoring arrangement flags
  - clears leading/trailing/excess bytes and maps anonymous memory for bss extension on MMU

## Core Dump Support
Under `CONFIG_ELF_CORE`:
- Adds FDPIC load map addresses to `elf_prstatus_fdpic`.
- Builds thread status notes with register and optional fpreg data.
- Writes ELF header, note phdr, PT_LOAD phdrs for VMAs, extra core phdr/data, notes, and dumped VMA ranges.
- Supports extended program header numbering through a synthetic section header.

## Research Notes
This file parallels `binfmt_elf.c` but has FDPIC-specific state: executable/interpreter load maps, per-segment runtime addresses independent from virtual addresses, and NOMMU-specific mapping paths.
