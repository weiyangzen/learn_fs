# File Research: sources/virtualization/spdk/lib/nvmf/transport.h

Internal header for the SPDK NVMf transport framework. It exposes common transport-layer helper functions to the NVMf core and concrete transport implementations.

Key responsibilities:
- Declares listener discovery delegation.
- Declares transport poll-group lifecycle helpers: create, optimal selection, destroy, pause, resume, add, remove, and poll.
- Declares generic request free/complete dispatchers.
- Declares qpair finalization and transport-id lookup helpers for peer, local, and listen addresses.
- Declares transport-level qpair abort dispatch.
- Declares shared iobuf helpers for normal request buffers, stripped DIF buffers, and aborting queued buffer acquisition.

Important behavior:
- This header is intentionally narrow: it does not define transport structs or inline behavior, only cross-module internal entry points.
- It separates public transport API headers from private NVMf core-to-transport glue.
- The buffer helper declarations show that shared iobuf allocation and stripped-buffer handling are centralized in `transport.c`, while concrete transports decide when to request or release them.

Dependencies:
- Includes SPDK standard, NVMe, NVMf, and NVMf transport public headers.
- Used by generic NVMf internals and transport backends such as TCP.

Notable risks:
- Function declarations here are part of an internal ABI between NVMf core files and transport implementations; signature drift requires coordinated updates across the NVMf library.
