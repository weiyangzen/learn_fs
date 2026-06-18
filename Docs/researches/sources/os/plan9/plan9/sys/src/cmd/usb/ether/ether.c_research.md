# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/ether.c

Implements the generic USB Ethernet adapter runtime and per-device file tree. It registers `etherU%d` subtrees with the USB 9P directory framework and exposes Plan 9 ether-style files including `clone`, `addr`, `stats`, `ifstats`, per-connection `data`, `ctl`, `type`, and stats files.

Key structures and behavior:
- Maintains a static VID/DID `cinfo[]` table for ASIX and SMSC controllers, with CDC Ethernet used as fallback through the `ethers[]` reset chain.
- Uses `Ether`, `Conn`, and `Buf` abstractions from `ether.h` to multiplex packets to multiple user connections.
- `newconn`, `fsopen`, `fsread`, `fswrite`, and `fsclunk` implement connection lifecycle and file operations.
- `etherctl` supports `connect`, `nonblocking`, `promiscuous`, `headersonly`, `addmulti`, and `remmulti`, then delegates unknown controls to controller-specific `ctl`.
- Read/write worker processes move buffers between USB bulk endpoints and connection queues.
- `etherinit` discovers CDC-style endpoints, including CDC union descriptor handling; `openeps` opens bulk endpoints.
- `kernelproxy` tries to bind the USB Ethernet device through `#l0/ether0/clone`; if that succeeds, no user-space `etherU%d` tree is needed.

Important interactions:
- Depends on `usb/lib` for `Dev`, endpoint opening, control requests, and `Usbfs`.
- Controller-specific reset functions may install custom `bread`, `bwrite`, `promiscuous`, `multicast`, and stats hooks.
- On fatal read errors it detaches the kernel USB endpoint, tears down the file tree with `usbfsdel`, and closes references.

Notable risks/quirks:
- Comments call out that this should ideally use `/dev/etherfile`.
- Multicast/loopback behavior is incomplete; loopback currently keys mainly off promiscuous state.
- Always defaults to configuration/interface choices found by scanning descriptors, with limited policy.
