# File Research: sources/os/plan9/9front/sys/src/9/port/portdat.h

Central portable kernel data-structure header for the 9front port layer.

Key contents:
- Forward-declares major kernel types and marks selected incomplete types.
- Defines lock, reference, rendezvous, qlock, rwlock, alarm, channel, path, device, directory, walk, mount, note, page, swap allocator, PTE, physical segment, segment, segio, image, process group, rendezvous group, environment group, file group, page allocator, wait queue, timer, scheduler queue, process, log, command buffer/table, UART, performance, watchdog, watchpoint, and per-mach portable state.
- Defines channel access flags, block flags, segment flags, process clone flags, process states, proc-control values, scheduler priority constants, queue state bits, global externs, and format pragmas.
- Defines key macros such as `BLEN`, `BALLOC`, `pagedout`, `swapaddr`, `PGHASH`, `MOUNTH`, and `REND`.

Role:
- This is the structural ABI tying together VM, VFS, process scheduling, device I/O, queues, timers, notes, environments, mounts, and architecture-specific process/MMU/FPU state.

Notable dependencies:
- Includes `<fcall.h>` and relies on architecture-provided `Mach`, `Label`, `Conf`, `Ureg`, `PFPU`, and `PMMU` definitions.
- Many fields are used by assembly or architecture code and are therefore layout-sensitive.

Notable risks:
- The header is a global coupling point: small field/layout changes can affect process switching, traps, MMU, devproc, and drivers.
- Comments identify several state fields as known to assembly or used for specific subsystems.
