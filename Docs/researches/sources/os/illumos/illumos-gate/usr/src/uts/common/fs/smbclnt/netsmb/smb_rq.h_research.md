# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_rq.h

## Purpose
Defines SMB request, transaction2, and NT transaction data structures, request state/flag constants, and request/transaction API declarations.

## Key Elements
Request flags cover allocation, sent state, restartability, interrupt behavior, multi-packet transactions, internal IOD requests, send/receive waiting, no-reconnect requests, more-data status, compound SMB2 requests, async replies, reconnect detection, and encrypted replies. `enum smbrq_state` tracks request lifecycle from not sent through notified.

`struct smb_rq` contains queue linkage, lock/CV, VC/share/owner pointers, SMB1 header fields, SMB2 request fields, compound linkage, message IDs, request and reply chains, credentials, timeout/retry state, local and protocol errors, parsed SMB1 reply fields, and parsed SMB2 reply metadata. `struct smb_t2rq` and `struct smb_ntrq` hold SMB1 transaction and NT transaction setup/parameter/data chains, limits, source layer, current request pointer, share pointer, and preserved raw error details.

The header declares request allocation/init/done, header filling, word/byte count helpers, simple/internal execution, SMB1-to-SMB2 negotiate response parsing, transaction allocation/init/done/request routines, and named-pipe transaction helper `smb_t2_xnp`.

## Dependencies
Includes `mchain.h`, queue definitions, and forward declarations for SMB connection/request structures. Consumers depend on IOD and protocol modules implementing the declared APIs.

## Behavior/Risks
The structure layout is shared across IOD, SMB1 helpers, SMB2 helpers, signing, encryption, and user ioctl paths. Flag semantics are subtle: no-interrupt flags protect server resource accounting, internal requests avoid reconnect recursion, and multi-packet requests remain queued across multiple replies. Compound SMB2 requests require correct linkage and credit/message-ID accounting by the IOD.
