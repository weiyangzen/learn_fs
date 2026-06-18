# File Research: sources/local-fs/ocfs2-tools/ocfs2.pc.in

This pkg-config template describes the userspace `libocfs2` library. It substitutes prefix, exec prefix, libdir, includedir, and version, declares dependencies on `o2dlm`, `o2cb`, and `com_err`, and exposes `-locfs2 -laio` plus include flags.

Consumers use this to compile/link external programs against OCFS2 userspace libraries.
