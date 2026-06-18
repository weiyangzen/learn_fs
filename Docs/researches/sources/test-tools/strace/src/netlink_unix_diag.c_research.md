<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_unix_diag.c -->
# sources/test-tools/strace/src/netlink_unix_diag.c

Purpose: decodes AF_UNIX sock_diag requests and response attributes.

Important APIs/types/functions: `decode_unix_diag_req`, `decode_unix_diag_msg`, `decode_unix_diag_vfs`, `decode_unix_diag_inode`, `decode_unix_diag_rqlen`, and `unix_diag_msg_nla_decoders`.

Control flow: request decoding prints family, protocol, state mask, inode, show flags, and cookie. Response decoding prints `unix_diag_msg`, then aligned attributes for name, VFS dev/inode, peer, peer inode array, queue lengths, meminfo, shutdown, and uid.

State and persistence behavior: no persistent state.

Dependencies and integration points: registered in `netlink_sock_diag.c`; depends on `<linux/unix_diag.h>`, `nlattr`, TCP state xlats, unix diag show/attr xlats, and device-number printers.

Risks: `UNIX_DIAG_ICONS` is decoded as an array of 32-bit inodes; kernel layout changes would require adjustment. Names rely on string attribute semantics.

Test signals: AF_UNIX request/response traces with all implemented attributes, state/show flags, multiple peer inodes, short payloads, and unknown attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_unix_diag.c -->
