# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_trantcp.c

## Scope

This file implements the NetBIOS session transport over TCP using illumos KTLI/TLI and STREAMS mblks.

## APIs And Behavior

- `nb_getmsg_mlen()` accumulates STREAMS messages until at least a requested byte length is available, handling `M_DATA`, TLI protocol indications, disconnects, orderly release, and timeouts.
- `nb_snddis()` sends a TLI disconnect request.
- `nb_sethdr()` writes the 4-byte NetBIOS session header.
- `nbssn_peekhdr()` waits for and validates a NetBIOS header without consuming it.
- `nbssn_recv()` reads a complete NetBIOS message, splits surplus data into `nbp_frag`, drops keepalives/zero-length messages, and returns session payloads.
- `smb_nbst_create()` opens a TCP or TCP6 KTLI endpoint and initializes `nbpcb`.
- `smb_nbst_done()` disconnects, closes the endpoint, frees addresses and credentials, and destroys locks.
- `smb_nbst_bind()`, `smb_nbst_unbind()`, and `smb_nbst_connect()` implement endpoint setup and transition to `NBST_SESSION`.
- `nb_disconnect()` clears connected state and sends disconnect once.
- `nbssn_send()` prepends or allocates a NetBIOS header and sends the mblk chain.
- `smb_nbst_send()` and `smb_nbst_recv()` serialize send and receive paths with `NBF_SENDLOCK` and `NBF_RECVLOCK`.
- `smb_nbst_setparam()` negotiates TCP/socket options through `t_koptmgmt()`.
- `smb_nbst_fatal()` classifies disconnect/reset/pipe errors as fatal.
- `smb_tran_nbtcp_desc` publishes this implementation through `smb_tran_desc`.

## State And Dependencies

- Uses `struct nbpcb` from `smb_trantcp.h`, `t_kopen`, `t_kconnect`, `tli_send`, `tli_recv`, `t_kspoll`, STREAMS mblk helpers, and NetBIOS constants.
- `nbp_frag` stores surplus received data after message splitting.

## Risks And Invariants

- Receive and send functions assert that higher layers serialize each direction.
- Header validation rejects reserved bits, bogus packet types, and packets larger than `NB_MAXPKTLEN`.
- The receive loop treats 15-second inactivity as `ETIME`, feeding server-not-responding behavior.
- Any unexpected protocol indication can force disconnect and `ENOTCONN`.
