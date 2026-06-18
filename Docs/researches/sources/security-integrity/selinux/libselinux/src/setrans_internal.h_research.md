<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setrans_internal.h -->
# sources/security-integrity/selinux/libselinux/src/setrans_internal.h

## Purpose
Defines the private setrans client/server socket path and protocol constants.

## Important APIs, Types, And Functions
Defines `SETRANS_UNIX_SOCKET`, request IDs `RAW_TO_TRANS_CONTEXT`, `TRANS_TO_RAW_CONTEXT`, `RAW_CONTEXT_TO_COLOR`, and `MAX_DATA_BUF`.

## Control Flow
No executable logic.

## State And Persistence Behavior
No local state; constants describe IPC framing limits and endpoint location.

## Dependencies And Integration Points
Included by `setrans_client.c` and tied to the `mcstransd` protocol.

## Risks And Test Signals
Compatibility with daemon protocol and maximum buffer size are the key concerns. IPC tests should validate all function IDs and boundary response sizes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setrans_internal.h -->
