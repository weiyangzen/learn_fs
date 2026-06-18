# File Research: sources/os/bsd/dragonflybsd/sys/kern/imgact_elf.c

## Summary
Implements DragonFly BSD ELF image activation and ELF core dump generation. It validates ELF binaries, selects ABI brand information, maps loadable segments into a new process VM space, loads interpreters, builds auxiliary vectors, and writes ELF core/checkpoint metadata.

## Main Responsibilities
- Maintains the ELF brand registry via `__elfN(insert_brand_entry)`, `__elfN(remove_brand_entry)`, and `__elfN(brand_inuse)`.
- Validates ELF headers, program header placement, target class/data/version, and supported machine brands.
- Loads `PT_LOAD` segments from vnode-backed VM objects, including BSS expansion and final-page copy handling.
- Finds brand information through ABI notes, `EI_OSABI`, old FreeBSD header branding, interpreter path, or fallback brand sysctl.
- Handles ET_DYN/PIE base selection and optional interpreter path rewriting/emulation prefixes.
- Constructs DragonFly ELF auxargs in `__elfN(dragonfly_fixup)`.
- Generates ELF core files through `generic_elf_coredump`, including notes, VM segment headers, vnode file handles, signal state, and open-file checkpoint metadata.

## Key APIs
- Exec path: `exec_elf32_imgact` or `exec_elf64_imgact` through `EXEC_SET_ORDERED`.
- Loader helpers: `__elfN(load_section)`, `__elfN(load_file)`, `extract_interpreter`, `check_PT_NOTE`.
- Core dump path: `__elfN(coredump)`, `generic_elf_coredump`, `__elfN(corehdr)`, `__elfN(puthdr)`, `elf_putallnotes`, `elf_puttextvp`, `elf_putsigs`, `elf_putfiles`.

## Important Behavior
`__elfN(load_section)` maps file-backed text/data with copy-on-write and disables core dumping for read-only sections. When `memsz > filsz`, it creates anonymous backing for BSS and copies the file tail fragment into the anonymous page.

The main image activator rejects non-ELF files with `-1`, but returns errno after recognizing an ELF header. Program headers must fit in the first page. `PT_INTERP` strings and ABI notes may be read beyond the first page using `exec_map_page`.

For core dumps, writable or otherwise dumpable normal map entries become `PT_LOAD` segments. Additional checkpoint-oriented data is appended after notes: VM text/data info, vnode file handles for mapped vnode objects, signal dispositions, timers, masks, and selected open vnode file descriptors.

## State and Integration
Sysctls expose fallback brand and PIE-base behavior under `kern.elf32` or `kern.elf64`, plus legacy coredump mode under `debug`. The loader sets `p_sysent`, `p_osrel`, `entry_addr`, VM text/data sizing, and `imgp->auxargs`.

## Risks
Brand registry scanning is explicitly race-prone for unload checks. Program-header support is limited to headers fitting in the first page for the main executable. Core/checkpoint output depends on stable vnode file handles and can silently omit vnode handles when `VFS_VPTOFH` fails.
