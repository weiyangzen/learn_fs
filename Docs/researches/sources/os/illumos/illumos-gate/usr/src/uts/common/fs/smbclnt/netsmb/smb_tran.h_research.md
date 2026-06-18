# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_tran.h

## Scope

This header defines the netsmb transport abstraction and the known NetBIOS-over-TCP transport descriptor interface.

## APIs And Definitions

- Defines `SMBT_NBTCP` as the known transport type.
- Defines transport parameter IDs for TCP_NODELAY, TCP connect timeout, keepalive, send/receive buffer sizes, and receive timeout.
- `struct smb_tran_desc` is the transport vtable with callbacks for create, destroy, bind, unbind, connect, disconnect, send, receive, poll, get/set parameter, and fatal-error classification.
- `SMB_TRAN_*` macros dispatch through `vcp->vc_tdesc`.
- Declares `smb_tran_nbtcp_desc`.

## Dependencies

- Consumed by virtual circuit setup and transport implementations.
- Uses kernel socket and STREAMS types, and `struct smb_vc`.

## Risks And Invariants

- All transport operations assume `vc_tdesc` is initialized.
- The abstraction currently exposes one concrete transport, but callers are insulated from that via the vtable macros.
