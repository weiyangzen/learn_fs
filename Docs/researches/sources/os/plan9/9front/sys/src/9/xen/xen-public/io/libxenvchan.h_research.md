# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/libxenvchan.h

Imported Xen/Qubes-origin vchan shared-interface header.

Purpose:
- Defines the shared data structure for libxenvchan inter-domain communication over grant pages and event channels.

Key content:
- Uses LGPL license text, unlike many MIT-style Xen public headers.
- Explains that vchan uses a symmetric datagram-style ring interface with runtime-sized rings rather than `ring.h`’s fixed asymmetric macros.
- Defines `struct ring_shared` with consumer/producer indexes.
- Defines notify flags `VCHAN_NOTIFY_WRITE` and `VCHAN_NOTIFY_READ`.
- Defines `struct vchan_interface` with left/right rings, ring orders, client/server liveness, notify bits, and a flexible grant list.

Integration:
- Not used by visible 9front Xen runtime code.
- Vendored as part of the Xen public I/O ABI set.

Risks/notes:
- License differs from surrounding headers and should be tracked when redistributing.
- Runtime ring sizing and flexible grant list require careful bounds checks in implementations.
