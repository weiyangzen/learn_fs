# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sbpf.c

This is the BPF output backend for `ipsend`.

`initdevice()` opens a BPF device, verifies BPF version compatibility, binds it to an interface with `BIOCSETIF`, obtains kernel buffer length, allocates a buffer, sets read timeout, flushes BPF state, and returns the descriptor.

`sendip()` writes a complete link-layer frame to the BPF descriptor.

Important dependencies include `<net/bpf.h>`, BSD interface ioctls, and `ipsend.h`.

Implementation notes and risks:
- The allocated `buf` is not used by `sendip()` in this file.
- Device discovery differs depending on `_PATH_BPF`.
- Errors often exit the process rather than returning.
