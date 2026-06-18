<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/msghdr.c -->
# sources/test-tools/strace/src/msghdr.c

Purpose: decodes `msghdr` structures, control messages, and `sendmsg`/`recvmsg` syscalls.
Important APIs/types/functions: `print_struct_msghdr`, `decode_msg_control`, `print_cmsg_type_data`, cmsg printer arrays for `SCM_*` and `IP_*`, `get_optmem_max`, `dumpiov_in_msghdr`, `SYS_FUNC(sendmsg)`, and `SYS_FUNC(recvmsg)`.
Control flow: fetches msghdr, decodes sockaddr/name length changes, chooses netlink-aware iovec printing, bounds control buffer by `/proc/sys/net/core/optmem_max`, walks aligned cmsg headers, and decodes known ancillary data by level/type.
State and persistence behavior: caches optmem_max statically and saves entry-side `msg_namelen` in `tcb` private ulong for recvmsg. Dependencies and integration points: socket syscalls, mmsghdr vector decoder, netlink decoder, fd printers, and time printers.
Risks: cmsg alignment differs by word size; malformed lengths and huge control buffers must be bounded. Test signals: SCM_RIGHTS/CREDENTIALS/PIDFD, timestamps old/new, IP_PKTINFO/RECVERR, truncated control buffers, netlink payloads, and namelen change tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/msghdr.c -->
