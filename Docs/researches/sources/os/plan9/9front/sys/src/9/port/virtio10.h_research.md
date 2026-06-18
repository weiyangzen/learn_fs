# File Research: sources/os/plan9/9front/sys/src/9/port/virtio10.h

Shared definitions for modern Virtio 1.0 PCI transport.

Key responsibilities:
- Defines Virtio status bits, feature bit `Fversion1`, common configuration offsets, and `Vio` register-space abstraction.
- Defines vring structures: `Vring`, `Vdesc`, and `Vused`.
- Declares typed register accessors `vin*`/`vout*`, `virtiomapregs()`, and `virtiounmap()`.

Dependencies:
- Used by modern virtio drivers and by machine-specific transport access files.

Notable behavior:
- Comments document that most architectures use memory BAR access through `virtio10mem.c`, while x86 has separate I/O-port handling.
