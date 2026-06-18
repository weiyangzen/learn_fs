# File Research: sources/os/plan9/9front/sys/src/9/xen/sdxen.c

Xen virtual block device frontend for Plan 9 `sd`.

Purpose:
- Implements `SDifc sdxenifc` for Xen VBDs.

Key behavior:
- Discovers likely Xen disk IDs from Linux major-device encodings.
- `xenverify` checks xenstore backend presence, allocates controller/ring/frame, event channel, and reads backend sector metadata.
- `backendconnect` publishes ring ref/event channel and waits for backend `Connected`.
- `xenonline` enables interrupts and marks frontend connected.
- `xenbio` serializes I/O, shares one page at a time, sends a single-segment block request, waits for interrupt completion, ends grant, and copies through an aligned bounce frame when needed.
- `sdxenintr` consumes block responses and wakes waiters.

Filesystem relevance:
- Provides the block device layer used by partitions and filesystems inside the Xen guest.

Risks/notes:
- Comments identify the implementation as simple and not performance-oriented.
- Single-page/single-request path limits throughput and relies on a bounce buffer for unaligned I/O.
- Ring overflow and richer `rio` paths are not implemented.
