# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_checkpoint.c

## Summary
Implements process checkpoint freeze/thaw support using ELF core-style files. It can write a checkpoint through the generic ELF core dump path and restore process registers, signals, VM mappings, and selected vnode-backed file descriptors.

## Main Responsibilities
- Implements `sys_checkpoint` for `CKPT_FREEZE` and `CKPT_THAW`.
- Reads and validates ELF headers/program headers from checkpoint files.
- Restores ELF notes into register/fpreg/process-name state.
- Restores signal actions, timers, signal masks, and parent signal.
- Restores VM text/data sizing and vnode-backed mappings from stored file handles.
- Restores selected open vnode file descriptors.
- Generates checkpoint filenames from `kern.ckptfile`.

## Important Behavior
Freeze requires membership in `kern.ckptgroup` unless it is `-1`. Direct freeze can use a supplied writable fd or the signal-handler path, which expands a filename, unlinks any previous checkpoint file, opens a new `0600` file with `O_NOFOLLOW`, stops other threads, and calls `generic_elf_coredump`.

Thaw requires a readable fd and current-process restore. It parses the ELF core header, notes, vnode mapping table, signal info, file descriptor info, then maps saved program segments. Restored mappings may be backed by original vnode handles or by the checkpoint file itself.

## Filesystem/VFS Signals
Checkpoint restore depends heavily on file handles: `ckpt_fhtovp` resolves `fhandle_t` through `vfs_getvfs` and `VFS_FHTOVP`, and vnode-backed mappings are reopened with `fp_vpopen`.

## Risks
The implementation has explicit limitations around multiple LWPs and non-vnode descriptors. Restore can fail if mounts or file handles are stale. The fd restore path closes descriptors `>= 3`, so it is intentionally destructive to the restoring process's current descriptor table.
