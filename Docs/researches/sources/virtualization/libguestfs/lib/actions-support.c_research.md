# File Research: sources/virtualization/libguestfs/lib/actions-support.c

## Role
Provides support helpers for generated host-side action wrappers.

## Main Operations
- `guestfs_int_check_reply_header()` validates protocol program, version, direction, procedure number, and serial number for daemon replies.
- `guestfs_int_check_appliance_up()` rejects daemon calls before launch or while launching.
- `guestfs_int_trace_open()` opens a trace buffer, falling back to stderr if `open_memstream()` fails.
- `guestfs_int_trace_send_line()` emits trace text through `GUESTFS_EVENT_TRACE`.

## Filesystem/Storage Relevance
This file safeguards the RPC protocol used by all host-to-appliance filesystem and block-device actions.
