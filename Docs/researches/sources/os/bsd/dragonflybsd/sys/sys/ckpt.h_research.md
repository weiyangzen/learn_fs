# File Research: sources/os/bsd/dragonflybsd/sys/sys/ckpt.h

Kernel-only checkpoint file format/state header.

Key responsibilities:
- Defines maximum checkpointed threads as 256.
- Defines checkpoint file header, VM layout info, file descriptor/file-handle state, and signal/action state structures.
- Defines `CKFIF_ISCKPTFD` to mark the checkpoint file descriptor itself.
- Defines `struct vn_hdr` only when ELF word size is known, pairing vnode file handle with an ELF program header.
- Provides debug trace/printf macros under `_KERNEL` and `DEBUG`.

Dependencies:
- Kernel-only; includes `sys/types.h`, `sys/mount.h`, and `sys/signalvar.h`.
- Uses `fhandle_t`, `sigacts`, `itimerval`, `sigset_t`, and ELF program headers.

Notable risks:
- Header explicitly errors if included outside kernel/kernel-structures contexts.
- File-format structs contain reserved fields but no versioning beyond an unimplemented magic comment.
