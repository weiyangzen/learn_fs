# File Research: sources/os/linux/linux/io_uring/napi.h

Header and stubs for io_uring NAPI integration.

Key contents:
- Under `CONFIG_NET_RX_BUSY_POLL`, declares init/free/register/unregister, dynamic NAPI ID add, wait busy loop, and SQPOLL busy poll.
- `io_napi_add()` extracts a socket from the request file and dynamically records its `sk_napi_id` only when dynamic tracking is active.
- Without busy-poll config, all helpers become no-op or `-EOPNOTSUPP` stubs.
