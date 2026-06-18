# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/netbios.h

Defines NetBIOS/NBNS/NBSS constants, wire structs, runtime structs, globals, and function prototypes.

Major contents:
- NBNS constants for ports, retries, opcodes, flags, rcodes, question/resource types/classes.
- `NbName`, `NbnsMessageQuestion`, `NbnsMessageResource`, `NbnsMessage`, and `NbnsTransaction`.
- `NbnsAlarm` timer abstraction.
- `NbSession`, `NbScatterGather`, and session-service I/O prototypes.
- `NbDgram` and `NbDgramSendParameters`.
- Local/remote name table APIs.
- `NbGlobals` with local IP, broadcast IP, and local NetBIOS name.

Interactions:
- Included by all NetBIOS files and indirectly by most Aquarela SMB files through `headers.h`.

Notable details:
- Uses Plan 9 IPv6-format `IPaddrlen` arrays while NetBIOS wire protocol carries IPv4 addresses.
