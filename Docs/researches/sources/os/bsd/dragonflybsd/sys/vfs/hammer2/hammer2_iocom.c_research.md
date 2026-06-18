# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_iocom.c

## Purpose
Integrates HAMMER2 with DragonFly's kernel DMSG/KDMSG communication layer. It initializes link communication, reconnects a mount to a file descriptor, advertises local PFS spans, receives remote spans, and transmits volume-copy configuration messages.

## I/O Communication Setup
- `hammer2_iocom_init()` initializes `hmp->iocom` with automatic LNK_CONN and automatic receive-side LNK_SPAN handling, but not automatic transmit-side spans because HAMMER2 advertises multiple PFSs itself.
- `hammer2_iocom_uninit()` tears down KDMSG state if message memory exists.
- `hammer2_cluster_reconnect()` installs a new communications file pointer, initializes automatic LNK_CONN fields, sets peer type to HAMMER2, restricts peer mask to HAMMER2 peers, assigns a host/mount label, and starts autoinitiation.

## Message Receive Handling
- `hammer2_rcvdmsg()` currently supports debug shell message scaffolding:
  - `DMSG_DBG_SHELL` receives `NOSUPP`.
  - `DMSG_DBG_SHELL | DMSGF_REPLY` prints auxiliary debug data.
  - Other transaction-creating messages receive `NOSUPP`; one-way and link-error messages are ignored to avoid reply loops.

## Automatic Link Handling
- `hammer2_autodmsg()` is called after KDMSG automatic LNK processing.
- On LNK_CONN replies to HAMMER2's auto-CONN, it:
  - Locks voldata.
  - Sends `DMSG_LNK_HAMMER2_VOLCONF` updates for nonempty copyinfo slots.
  - Unlocks voldata.
  - Calls `hammer2_update_spans()` to advertise local PFSs.
- On received LNK_SPAN create messages, it accepts only HAMMER2 peer type and protocol version 1, terminates the peer label string, optionally logs debug info, and replies with success.
- On LNK_SPAN delete messages, it relies on KDMSG automatic delete replies and optionally logs debug output.

## Span Advertisement
- `hammer2_update_spans()` locks the media-local super-root inode, scans its child chains, and for each inode creates a `DMSG_LNK_SPAN | DMSGF_CREATE` message.
- It fills span peer ID from PFS cluster ID, PFS ID from PFS filesystem ID, PFS type from inode metadata, peer type HAMMER2, protocol version 1, and peer label from the PFS filename.
- Reply handling for transmitted spans is `hammer2_lnk_span_reply()`, which replies to remote delete requests if the local transaction is not already deleting.

## Volume Configuration Updates
- `hammer2_volconf_update()` sends one `DMSG_LNK_HAMMER2_VOLCONF` message over the open connection transaction when `conn_state` exists.
- The message carries the selected copyinfo slot, media fsid, and index.
- The code notes missing interlocking against connection state termination.

## Current Limitations
- Remote PFS support is mostly connection and advertisement plumbing in this file; object-level remote PFS operations are described in comments but not implemented here.
- Unsupported DMSGs are deliberately rejected.
- Several peer-type and client-mode filters are disabled behind `#if 0`.
- `hammer2_update_spans()` has a loop hazard: if a non-inode chain is encountered, the `continue` path does not advance to the next chain in the visible code.
