## sources/user-network-fs/samba/source3/lib/tallocmsg.c

Purpose: messaging hook that lets another process request a talloc memory report from a Samba process via `MSG_REQ_POOL_USAGE`.

Important functions are private `pool_usage_filter` and public `register_msg_pool_usage`. The filter expects exactly one passed file descriptor and writes `talloc_full_report_printf(NULL, f)` to it.

Control flow: `register_msg_pool_usage` starts a persistent `messaging_filtered_read_send` request on the message context’s tevent loop using `pool_usage_filter`. The filter ignores other message types, validates fd count, wraps the fd with `fdopen_keepfd`, writes the talloc report, closes the stdio stream, and returns false so the filtered read remains active rather than completing.

State and persistence: no durable state. The persistent tevent request is owned by the supplied `mem_ctx`; reports are emitted to caller-supplied fd. Dependencies are Samba messaging, tevent, talloc reporting, debug, and `fdopen_keepfd`.

Risks: a requester with messaging access can trigger potentially large memory reports and learn allocation layout. The code expects exactly one fd; missing fd just logs and ignores. Closing the `FILE *` around `fdopen_keepfd` should not close the original fd, matching helper semantics. Tests should cover registration failure, message type filtering, bad fd counts, repeated requests, and report output to an fd.
