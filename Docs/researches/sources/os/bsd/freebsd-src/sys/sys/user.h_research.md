# File Research: sources/os/bsd/freebsd-src/sys/sys/user.h

Public process, file descriptor, VM map, VM object, kstack, knote, and VM layout export ABI header.

Key responsibilities:
- Defines `struct kinfo_proc`, the central `KERN_PROC` export record, with extensive process, credential, signal, VM, scheduling, timing, jail, tracing, priority, rusage, PCB, kstack, path, thread, and spare fields.
- Defines legacy `struct user` for a.out core dumps and compatibility aliases.
- Defines file-descriptor export constants for file types, vnode types, special fd records, ntsync types, and file flags.
- Defines legacy `struct kinfo_ofile` and current `struct kinfo_file`, including unions for sockets, vnodes/files, semaphores, pipes, ptys, proc descriptors, eventfd, timerfd, jaildesc, kqueue, inotify, and ntsync details.
- Defines lockf export record and constants.
- Defines VM map entry types, protection bits, flags, legacy/current VM map entry structures, VM object flags and record, kstack record, signal trampoline record, VM layout flags/record, and knote record.
- Under `_KERNEL`, declares sysctl packing/output helpers for proc, filedesc, cwd, vmmap, kqueues, vnode-type conversion, and kinfo packing.

Dependencies:
- Pulls in machine PCB, process, VM, resource, signal, socket, queue, ucred, uio, mutex/lock, event, time, and caprights definitions depending on kernel/user build.

Notable risks:
- Many structures have fixed-size compatibility warnings; changing sizes can break existing binaries unless a new MIB/ABI path is provided.
- New fields must consume spare areas matching alignment and size across all supported architectures, and initialization must be added in both kernel and libkvm paths.
