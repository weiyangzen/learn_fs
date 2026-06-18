# File Research: sources/os/plan9/plan9/sys/src/9/port/portdat.h

Central portable data-structure contract for the Plan 9 kernel port layer.

Major contents:
- Common typedefs for kernel objects: `Chan`, `Dev`, `Block`, `Queue`, `Page`, `Segment`, `Proc`, `Pgrp`, `Fgrp`, `Rgrp`, `Image`, `Timer`, `Uart`, and many others.
- Numeric helpers and bitfield macros: `HOWMANY`, `ROUNDUP`, `ROUNDDN`, `ROUND`, `PGROUND`, `FIELD`, `FEXT`, `FINS`, etc.
- Synchronization structures: `Ref`, `Rendez`, `QLock`, `RWlock`.
- Device/channel structures: `Chan`, `Path`, `Dev`, `Dirtab`, `Walkqid`.
- Mount namespace structures: `Mount`, `Mhead`, `Mnt`, `Mntwalk`.
- VM structures: `Page`, `Swapalloc`, `Image`, `Pte`, `Physseg`, `Sema`, `Segment`.
- Process structures: `Pgrp`, `Rgrp`, `Egrp`, `Fgrp`, `Proc`, `Schedq`, `Waitq`.
- Timer and scheduling constants, process states, rfork flags, segment indices, priority levels.
- Global externs for kernel configuration, device table, queues, swap image, syscall names, and system identity.
- UART, performance, watchdog, watermark, command parsing, and queue state structures/constants.

Notable details:
- `struct Proc` embeds scheduler state, memory segments, fd/env/namespace/rendez groups, note/debug state, timer state, MMU-private state, and syscall trace storage.
- `struct Segment` embeds a semaphore list used by user semaphores.
- `struct Swapalloc swapalloc` is defined in this header, not merely declared.
- Queue state bits `Qstarve`, `Qmsg`, `Qclosed`, `Qflow`, `Qcoalesce`, and `Qkick` are shared with `qio.c`.

Role:
- This file is a dependency hub; most port C files include it and rely on its exact layouts.
