# sources/security-integrity/selinux/libselinux/src/avc_internal.c

Purpose: `avc_internal.c` provides AVC support glue for SELinux netlink/status events. It owns callback-function globals, enforcing/running state, netlink socket lifecycle, and translation of kernel setenforce/policyload notifications into AVC cache resets and user callbacks.

Important APIs/types/functions: global callback pointers include `avc_func_malloc`, `avc_func_log`, thread callbacks, and lock callbacks. Public internal functions include `avc_process_setenforce()`, `avc_process_policyload()`, `avc_netlink_open()`, `avc_netlink_close()`, `avc_netlink_check_nb()`, `avc_netlink_loop()`, `avc_netlink_acquire_fd()`, and `avc_netlink_release_fd()`.

Control flow: setenforce events log the transition, update `avc_enforcing` unless caller fixed it via `AVC_OPT_SETENFORCE`, reset the AVC when moving to enforcing, and call `selinux_netlink_setenforce()`. Policyload events reset cache with the sequence number, flush class cache, and call `selinux_netlink_policyload()`. Netlink open creates a `NETLINK_SELINUX` socket, optionally nonblocking, and binds `SELNL_GRP_AVC`. Receive uses `poll()` and `recvfrom()`, validates kernel origin, length, truncation, and message type, then dispatches supported notification records.

State and persistence: module state is the static netlink `fd`, AVC globals, thread/main-loop flags, and callback function pointers. The socket persists until close, thread exit, or destroy.

Dependencies and integration: uses Linux netlink headers, `selinux_netlink.h`, `selinux_status` consumers, AVC cache control functions from `avc.c`, and application main loops that can acquire the netlink fd.

Risks and test signals: spoofed/truncated netlink packets must be rejected. Nonblocking polling must return `EWOULDBLOCK` cleanly. Tests should simulate setenforce/policyload messages, malformed `nlmsg_len`, non-kernel `nl_pid`, app-main-loop fd acquisition, and callback failures.
