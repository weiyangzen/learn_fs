# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vtrace.h

## Role

`vtrace.h` preserves legacy vtrace facility and event IDs and maps enabled trace macros to DTrace static probes in debug/lint builds. The comments state that vtrace has been subsumed by DTrace and that new tracepoints should use DTrace directly.

## Key Contents

The header defines facility IDs for traps, interrupts, dispatcher, VM, process, STREAMS, TCP, UDP, IP, ARP, Ethernet drivers, SCSI, callout, filesystems, kernel RPC, scheduling, physical I/O, meta disk, sockfs, devmap, and DADA/IDE target paths.

It then defines event tags for each facility. Major groups include:
- trap and interrupt entry/exit points,
- dispatcher scheduling/switching/preemption events,
- VM pageout, segmap, segvn, anon, swap, page creation/free/hash events,
- process exec/exit/fork,
- scheduler swap-in/swap-out decisions,
- STREAMS queue/message events,
- TCP/UDP/IP/ARP open/close/read/write/service events,
- legacy Ethernet driver events,
- physio lock/fault/buffer phases,
- SCSI ESP/ISP/FAS and sd path events,
- callout timeout/untimeout events,
- specfs/tmpfs/swapfs/UFS/NFS/KRPC events,
- FIFO/rlogin/sockfs/devmap/DAD events.

## Trace Macros

When `DEBUG`, `lint`, or `__lint` is defined, `TRACE_0` through `TRACE_5` expand to calls to generated `__dtrace_probe___vtrace_<tag>()` functions with up to five `ulong_t` arguments.

Otherwise, all `TRACE_*` macros compile away.

## Research Notes

The numeric constants are historical compatibility data and comments say they should not be changed or extended. Consumers should treat this as an observability compatibility layer, not as a modern tracing API.
