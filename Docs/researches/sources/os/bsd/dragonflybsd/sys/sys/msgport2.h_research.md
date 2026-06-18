# File Research: sources/os/bsd/dragonflybsd/sys/sys/msgport2.h

Kernel inline helpers for LWKT message and port operations.

Key responsibilities:
- Declares `M_LWKTMSG` malloc type when `MALLOC_DECLARE` is available.
- Provides inline message initialization helpers:
  - `lwkt_initmsg`
  - `lwkt_initmsg_abortable`
- Provides inline wrappers for reply, get, wait, check, drop, and receipt setup operations.
- Routes operations through the target/reply port callback table.

Important behavior:
- `lwkt_initmsg()` does not zero the whole message; it only initializes flags and reply port.
- Initialized messages are marked `MSGF_DONE` until sent.
- `lwkt_dropmsg()` asserts `MSGF_DROPABLE`, then calls the current target port's drop hook if present.
- `lwkt_setmsg_receipt()` sets `MSGF_RECEIPT` and stores a callback.

Dependencies:
- Kernel-only; rejects userland inclusion.
- Includes `sys/systm.h`.
- Requires `msgport.h` definitions and error constants such as `ENOENT`.

Notable risks:
- Because initialization is partial, stale fields must be initialized by callers before use.
- Replying assumes `ms_reply_port` is valid and has a correct `mp_replyport` method.
