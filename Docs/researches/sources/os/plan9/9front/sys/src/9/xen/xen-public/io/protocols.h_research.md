# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/protocols.h

Imported Xen public I/O protocol ABI string definitions.

Purpose:
- Defines the xenstore protocol ABI strings used by split-device frontends/backends to agree on ring structure layout.

Key content:
- Defines ABI strings for x86_32, x86_64, and ARM.
- Defines `XEN_IO_PROTO_ABI_NATIVE` based on compile-time architecture.
- Emits a compile error for unsupported architectures.

Integration:
- Referenced by `blkif.h` xenstore protocol documentation.
- Important when front/back ends run with different machine ABIs.

Risks/notes:
- Protocol string mismatch causes peers to interpret ring structures incorrectly.
