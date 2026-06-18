# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crtend.S

OR1K section terminator object. It defines hidden/global `__EH_FRAME_END__` and `__JCR_END__` symbols with 4-byte-aligned padding.

No legacy `.ctors/.dtors` endpoints are emitted because NetBSD OR1K uses array constructors.
