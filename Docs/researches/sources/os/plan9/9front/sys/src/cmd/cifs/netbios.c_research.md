# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/netbios.c

Implements NetBIOS name service/session support and packet debugging for CIFS over NetBIOS. It includes local byte-get/put helpers, NetBIOS name encoding, called-name discovery, TCP session setup, NetBIOS-framed RPC I/O, and hex/protocol dumps.

`calledname` sends a UDP/137 adapter status query for `*`, parses returned NetBIOS names, and selects a non-group workstation/service name. `nbtdial` opens TCP/139, performs NetBIOS session request, handles positive/negative/keepalive/retarget packets, and returns a connected fd.

`nbthdr` initializes a packet with a NetBIOS session header. `nbtrpc` fills payload length, writes the full packet, reads and validates response headers, skips keepalives, enforces MTU, and returns packet length.

`xd` is a debugging dumper. It can append raw bytes to `pkt.log`, decode SMB header fields, print Trans2 request/response header fields, and translate SMB errors through `nterrstr` or `doserrstr`.

Important dependencies: packet packing helpers from `pack.c`, global `Debug`, constants from `cifs.h`, and Plan 9 networking via `netmkaddr`, `dial`, `readn`, `alarm`.

Risk notes: low-level parsing assumes packet layouts and uses fixed buffers; debugging code decodes selected SMB forms rather than a complete protocol parser.
