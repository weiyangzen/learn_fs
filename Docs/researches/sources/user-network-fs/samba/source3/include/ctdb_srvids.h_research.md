# sources/user-network-fs/samba/source3/include/ctdb_srvids.h

## Purpose
`ctdb_srvids.h` defines Samba's static CTDB service IDs in the reserved `0xFE...` range for clustered messaging.

## Important APIs, Types, And Functions
- `CTDB_SRVID_SAMBA_NOTIFY_PROXY` identifies the process receiving clustered file change notifications and multicasting them locally.
- `CTDB_SRVID_SAMBA_PROCESS` identifies Samba processes for broadcast-style messaging.
- A disabled block documents `CTDB_SRVID_SAMBA_NOTIFY`, already provided by CTDB protocol headers for global lock death notifications.

## Control Flow
No executable flow. CTDB messaging code uses these constants when registering and sending messages.

## State And Persistence
No local state. The constants are distributed protocol identifiers and must remain globally unique.

## Dependencies And Integration Points
It integrates notify, messaging, and global lock subsystems with CTDB's service registration namespace.

## Risks
Changing or reusing IDs breaks clustered deployments. The disabled duplicate constant documents dependency on CTDB headers and should remain consistent.

## Test Signals
Cluster tests should verify notify proxy registration, message_send_all behavior, and no service ID collisions with CTDB protocol definitions.
