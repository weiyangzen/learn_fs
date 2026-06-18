# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_msgops.c

## Purpose
Contains minimal HAMMER2 debug/message operation handlers for kdmsg cluster messaging.

## Functions
`hammer2_msg_adhoc_input(kdmsg_msg_t *msg)` logs an ad-hoc input message command and returns success. It does not dispatch or mutate message state.

`hammer2_msg_dbg_rcvmsg(kdmsg_msg_t *msg)` handles debug-message commands:
- `DMSG_DBG_SHELL`: shell execution is not supported; replies `DMSG_ERR_NOSUPP`.
- `DMSG_DBG_SHELL | DMSGF_REPLY`: prints auxiliary reply text if present, forcing NUL termination at `aux_size - 1`.
- default: replies unsupported for unknown messages.

## Dependencies
Includes kernel headers and `hammer2.h`; depends on kdmsg command flags and `kdmsg_msg_reply()`.

## Integration Notes
This is defensive/stub-like support for debug kdmsg traffic. Shell command execution is intentionally unsupported. The reply path assumes `aux_data` is writable and `aux_size` is nonzero when present; callers should not pass malformed aux buffers.
