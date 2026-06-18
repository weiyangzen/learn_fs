# File Research: sources/teaching/minix/minix/servers/vfs/coredump.c

This file writes ELF core files for terminated processes.

Key entry point:
- `write_elf_core_file(struct filp *f, int csig, char *proc_name)`

Core dump construction:
- Builds one `PT_NOTE` program header plus up to `MAX_REGIONS` `PT_LOAD` headers.
- Fills ELF header using target ELF class/data/machine constants.
- Builds two MINIX notes:
  - process/core metadata (`NT_MINIX_ELFCORE_INFO`)
  - general registers (`NT_MINIX_ELFCORE_GREGS`)
- Gets memory regions from VM with `vm_info_region`.
- Adjusts offsets after headers are known.
- Writes ELF header, program headers, note contents, and memory segment contents through VFS write path.

Important interactions:
- Uses `sys_getregs` to get target registers.
- Uses `sys_datacopy_try` to copy target memory.
- Uses `read_write` on the provided core-file filp.

Notable implementation detail:
- If copying a segment chunk fails, the code zeroes the local buffer and then `continue`s, so it does not write the zero-filled chunk. The comment says missing memory should be written as zeroes, but the control flow skips the write.
