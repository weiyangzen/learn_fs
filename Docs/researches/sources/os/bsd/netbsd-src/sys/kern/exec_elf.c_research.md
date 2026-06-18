# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_elf.c

## Purpose
Shared machine-independent ELF executable loader implementation, included by the 32-bit and 64-bit ELF wrapper files after defining `ELFSIZE`.

## Main Interfaces
- `exec_elf_makecmds()` validates ELF headers, reads program headers, handles `PT_INTERP`, probes NetBSD ELF notes/emulation, builds VM commands for loadable segments, loads the interpreter, and sets the initial entry point.
- `elf_check_header()` validates magic, ELF class, machine IDs, flags, and program/section header counts.
- `elf_load_psection()` converts one `PT_LOAD` segment into `vmcmd_map_pagedvn`, `vmcmd_map_readvn`, and `vmcmd_map_zero` commands.
- `elf_load_interp()` opens and maps the dynamic loader, checking execute permissions, `MNT_NOEXEC`, and `MNT_NOSUID`.
- `elf_copyargs()` and `elf_populate_auxv()` append ELF auxiliary vectors, including program headers, page size, interpreter base, entry address, stack base, credentials, and optional `AT_SUN_EXECNAME`.
- `netbsd_elf_signature()`, `netbsd_elf_note()`, and `netbsd_elf_probe()` recognize NetBSD ELF notes and populate OS version, PaX, machine-arch, and machine code-model metadata.
- `elf_free_emul_arg()` releases the per-exec ELF argument block.

## Dependencies
Uses the NetBSD exec package, vnode/text marking, UVM VM command infrastructure, PaX ASLR/mprotect hooks, emulation path lookup, kauth credentials, ELF note definitions, and machine-dependent ELF macros.

## Implementation Notes
The file is template-style C: symbol names are remapped through `ELFNAME` macros so the same body emits `elf32_*` and `elf64_*` functions. Dynamic executables can be relocated by `elf_placedynexec()` using PaX ASLR offsets. Loadable writable segments get special tail handling because the paged vnode pager cannot zero-fill a partial final data page.

## Research Notes
This is central executable-loader code with strong ordering and cleanup requirements. Failure paths must release interpreter path buffers, free program-header storage, clear emulation args, and kill pending VM commands. Any change to program-header validation, interpreter placement, auxv sizing, or note parsing can affect native execution, compatibility emulations, ASLR, and set-id handling.
