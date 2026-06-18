<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_sock_diag.h -->
# sources/test-tools/strace/src/netlink_sock_diag.h

Purpose: declares sock_diag decoder signatures and shared inet sockid printing support.

Important APIs/types/functions: `DECL_NETLINK_DIAG_DECODER`, extern declarations for inet/netlink/packet/smc/unix request and message decoders, `print_inet_diag_sockid`, and `PRINT_FIELD_INET_DIAG_SOCKID`.

Control flow: no runtime flow; macro standardizes decoder prototypes.

State and persistence behavior: no state.

Dependencies and integration points: consumed by `netlink_sock_diag.c` and each family diag implementation.

Risks: all sock_diag family decoders depend on this prototype. The shared inet sockid printer assumes `struct inet_diag_sockid` layout from kernel headers.

Test signals: build coverage for each declared decoder plus inet sockid output in inet and SMC diag tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_sock_diag.h -->
