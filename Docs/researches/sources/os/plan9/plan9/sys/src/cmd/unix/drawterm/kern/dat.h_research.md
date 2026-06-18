# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/dat.h

Core data-structure header for drawterm’s user-space Plan 9 kernel facade.

Key contents:
- Defines constants and forward declarations for blocks, channels, devices, namespace groups, process groups, queues, rendezvous, mounts, logs, commands, and process state.
- Defines `Conf`, `Label`, `Ref`, `Rendez`, `RWlock`, `Block`, `Chan`, `Cname`, `Dev`, `Dirtab`, `Walkqid`, `Mount`, `Mhead`, `Mnt`, `Note`, `Pgrp`, `Rgrp`, `Egrp`, `Fgrp`, `Proc`, `Log`, `Cmdbuf`, and `Cmdtab`.
- Defines channel access modes, channel flags, block flags, mount/rendezvous hash sizing, fd sizing, process states, queue flags, and shared extern globals.
- Redefines `up` as `_getproc()` to support thread-local/current-process lookup.

Role in this group:
- The central ABI between drawterm’s kernel-like code, device implementations, namespace resolver, and GUI/input devices.

Notable risks:
- Many structures are reduced/adapted from the real Plan 9 kernel; code using them depends on drawterm-specific simplifications.
- `up` as a macro hides function calls and can surprise code expecting a global variable.
