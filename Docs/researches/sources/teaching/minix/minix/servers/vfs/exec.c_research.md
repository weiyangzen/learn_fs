# File Research: sources/teaching/minix/minix/servers/vfs/exec.c

This file implements VFS’s side of `exec`.

Key entry point:
- `pm_exec(path, path_len, frame, frame_len, pc, newsp, ps_str)`

Major responsibilities:
- Copies the user-provided stack frame into VFS before replacing the process image.
- Resolves the executable path and opens the vnode.
- Checks regular-file type and execute permission.
- Honors setuid/setgid bits when allowed.
- Reads the executable header.
- Detects scripts and patches the stack so the interpreter receives the script path and `#!` arguments.
- Detects dynamic ELF interpreters and switches execution to the interpreter.
- Opens the main executable as an FD for dynamic loaders (`AT_EXECFD` path).
- Optionally gives VM a duplicate FD for mmap-backed loading when the filesystem supports `RES_HASPEEK`.
- Uses `libexec` loaders, currently ELF.
- Reports new exec metadata to PM.
- Prepares ELF auxiliary vectors for dynamic executables.
- Copies the final stack into the new process image.
- Closes `FD_CLOEXEC` descriptors and updates effective credentials and process name.

Important helper functions:
- `get_read_vp`: opens/reopens the current executable vnode.
- `vfs_memmap`: callback into `minix_vfs_mmap` for VM-backed mappings.
- `stack_prepare_elf`: fills ELF auxiliary vector entries.
- `is_script`: recognizes `#!`.
- `patch_stack`: rewrites argv for scripts.
- `insert_arg`: inserts/replaces argv[0] in the stack image.
- `read_seg`: reads executable segments through the filesystem.
- `clo_exec`: closes close-on-exec descriptors.
- `map_header`: reads the initial header chunk.

Concurrency/locking:
- Serializes exec with VM using `lock_exec`.
- Uses path/vmnt/vnode locks through lookup structures.
- Cleans up VM fd if it was opened but not used.

Notable implementation detail:
- The old-style K&R definition of `patch_stack` is used.
- `stack_prepare_elf` depends on libc leaving reserved AuxVec space in the user stack frame.
