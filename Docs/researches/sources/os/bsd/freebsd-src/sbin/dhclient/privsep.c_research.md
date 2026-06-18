# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/privsep.c

## Purpose
Implements the simple message buffer and dispatcher used between the restricted dhclient process and privileged helper.

## Main Elements
- Buffer helpers:
  - `buf_open()` allocates a fixed-size buffer.
  - `buf_add()` appends bytes with bounds checking.
  - `buf_close()` writes the whole buffer to a socket/fd and frees it.
  - `buf_read()` reads an exact byte count or exits on short/failed reads.
- `dispatch_imsg()` handles:
  - `IMSG_SCRIPT_INIT`: reads medium/reason and calls `priv_script_init()`.
  - `IMSG_SCRIPT_WRITE_PARAMS`: reconstructs lease strings/options and calls `priv_script_write_params()`.
  - `IMSG_SCRIPT_GO`: runs script and sends return code.
  - `IMSG_SEND_PACKET`: delegates raw packet sending.
  - `IMSG_SET_INTERFACE_MTU`: changes interface MTU.

## Dependencies And Integration
Used by `dhclient.c`, `dispatch.c`, and `bpf.c` through `privsep.h`. The privileged child loops in `fork_privchld()` and calls this dispatcher.

## Risk Notes
The dispatcher performs length checks against the message header before allocation and reads, guarding corrupted messages. It exits fatally on protocol violations. `buf_read()`’s final short-read comparison is based on the decremented byte count, so its explicit short-read diagnostic is less useful than intended, but EOF/errors still exit.
