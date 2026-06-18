# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_protocol.h

This header defines 9P wire protocol constants and structures.

Key contents:
- `enum p9_cmds_t` lists 9P message type numbers for legacy, 9P2000.u, and 9P2000.L requests/responses.
- `enum p9_open_mode_t` defines Plan 9 open modes and flags.
- `enum p9_perm_t` defines Plan 9 permission/type bits.
- `enum p9_qid_t` defines qid type bits.
- Magic values include `P9PROTO_NOFID`, default uname/aname, `P9_NONUNAME`, and `P9_MAXWELEM`.
- Wire-visible structures:
  - `struct p9_qid`
  - `struct p9_statfs`
  - `struct p9_wstat`
  - `struct p9_stat_dotl`
  - `struct p9_iattr_dotl`
  - `struct p9_buffer`

Attribute masks:
- `P9PROTO_STATS_*` masks identify requested/returned getattr fields.
- `P9PROTO_SETATTR_*` masks identify valid setattr fields.
- `P9PROTO_UNLINKAT_REMOVEDIR` defines unlinkat directory removal semantics.

Research-relevant notes:
- This header is protocol-shared; changes affect both client request encoding and p9fs vnode attribute conversion.
- `p9_buffer` is not self-owning; it tracks raw memory supplied by the client layer.
