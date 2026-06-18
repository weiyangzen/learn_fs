# File Research: sources/os/plan9/plan9/sys/src/9/boot/boot.h

Shared declarations for boot program components.

Key contents:
- Defines `Method` with `name`, `config`, `connect`, and `arg`.
- Defines constants `Statsz` and `Nbarg`.
- Declares global boot state such as `bootdisk`, `rootdir`, `cfs`, `cpuflag`, `cputype`, `debugboot`, flags, methods, auth state, stats buffer, boot args, and `authaddr`.
- Declares utility, boot, auth, local/paq/embed/tcp config/connect, USB, partition, time, and old9p functions.
- Defines `dprint` conditional debug macro.

This header connects all `sys/src/9/boot` C files generated/linked into the architecture-specific boot binary.
