# File Research: sources/os/linux/linux/io_uring/notif.c

Zerocopy notification request implementation for network sends.

Key flows:
- `io_alloc_notif()` allocates an internal `io_kiocb`, initializes it as a NOP notification, takes task refs, and embeds `struct io_notif_data` with `ubuf_info`.
- `io_tx_ubuf_complete()` is the skb zerocopy completion callback. It tracks copied/used status, reference counts, linked notification chains, and schedules io_uring task_work when the head completes.
- `io_notif_tw_complete()` finalizes one or more linked notifications, sets usage reporting flags, unaccounts pinned memory, and completes each notification request.
- `io_link_skb()` attaches io_uring notification ubufs to skbs and can chain compatible notifications sharing context/task ownership.

Important details:
- Notification chains must share ring context and task context.
- Report-usage mode sets `IORING_NOTIF_USAGE_ZC_COPIED` if zerocopy was not used or copied fallback occurred.
- Memory accounting is released at notification completion.
