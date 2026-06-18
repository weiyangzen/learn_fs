# File Research: sources/os/linux/linux/io_uring/notif.h

Header for zerocopy notification data.

Key contents:
- `struct io_notif_data` embeds file pointer, `ubuf_info`, linked-list pointers for batching notifications, accounted pages, and zerocopy usage/copy reporting booleans.
- Defines `IO_NOTIF_UBUF_FLAGS` and splice batch size.
- `io_notif_to_data()` maps a notification request to embedded notification data.
- `io_notif_flush()` forces completion by calling `io_tx_ubuf_complete()`.
- `io_notif_account_mem()` charges pages against the ring user for non-fixed zerocopy send memory.
