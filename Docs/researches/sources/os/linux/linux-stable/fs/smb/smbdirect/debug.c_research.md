# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/debug.c

## Purpose
Legacy debug/proc reporting for SMBDirect connections.

## Main Function
- `smbdirect_connection_legacy_debug_proc_show()` writes connection state and counters into a `seq_file`.
- Reports:
  - protocol version and socket status
  - receive credit max, send credit target, max send/receive sizes
  - fragmented send/receive sizes
  - keepalive interval, max RDMA read/write size, caller-provided RDMA threshold
  - receive buffer get/put counters and empty-send counter
  - reassembly enqueue/dequeue counters and current queue state
  - current send/receive credits and pending sends
  - responder resources, FRMR depth, MR type
  - MR ready/used counts

## Notes
- Null socket input returns without output.
- It reads live atomics and counters without locking; this is diagnostic output, not a synchronization boundary.
- Exported as `smbdirect_connection_legacy_debug_proc_show`.
