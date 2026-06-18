# File Research: sources/os/bsd/openbsd-src/sys/kern/exec_elf.c

ELF executable loader and ELF core dump writer.

Key exec-loader behavior:
- `elf_check_header()` validates ELF magic, class, endianness, version, target machine, and program-header count.
- `elf_load_psection()` converts `PT_LOAD` segments into vmcmds, enforces W^X by withholding execute permission from writable segments, applies immutable mapping where safe, handles file-backed and zero-filled portions, and accounts for textrel/mutable sections.
- `elf_read_from()` reads from an executable vnode with `vn_rdwr`.
- `elf_load_file()` loads the dynamic linker/interpreter as `ET_DYN`, validates noexec mounts and read permission, maps segments, handles randomize/mutable/syscall-pin program headers, and marks text vnodes.
- `exec_elf_makecmds()` validates the main executable, rejects writable text vnodes with `ETXTBSY`, reads program headers, handles `PT_INTERP`, OpenBSD notes, PIE base randomization, `DT_TEXTREL`, segment sizing, syscall pin tables, aux args, and stack setup.
- `exec_elf_fixup()` loads the interpreter in phase II, processes vmcmds, and writes ELF auxiliary vector entries to user stack.
- OpenBSD note handling recognizes `PT_OPENBSD_WXNEEDED`, `PT_OPENBSD_NOBTCFI`, and profiling notes.

Key core-dump behavior:
- `coredump_elf()` writes ELF core files unless `SMALL_KERNEL`.
- Uses `uvm_coredump_walkmap()` to build program headers.
- Handles large segment counts with extended section-header layout.
- Writes OpenBSD notes for process info, auxv, optional write cookie, and per-thread register/fpreg data.
- Special-cases execute-only sigcode by writing from kernel mapping.

Filesystem/OS relevance:
- Central executable file-to-address-space path.
- Heavily uses vnodes, mount flags, `vn_rdwr`, text vnode marking, UVM mappings, immutable memory, syscall pinning, and coredump file emission.
