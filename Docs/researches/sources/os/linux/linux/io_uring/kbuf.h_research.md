# File Research: sources/os/linux/linux/io_uring/kbuf.h

Header for provided-buffer state and helpers.

Key contents:
- `struct io_buffer_list` represents either legacy `buf_list` or ring `buf_ring`, plus group id, head, mask, flags, incremental minimum-left threshold, and mapped region.
- `struct io_buffer` is the legacy buffer node with address, length, bid, and bgid.
- `struct buf_sel_arg` carries iovec output state for multi-buffer selection.
- Inline helpers decide whether buffer selection is needed, recycle ring/legacy buffers, and turn selected buffers into CQE flags through `io_put_kbuf()` / `io_put_kbufs()`.

The header is consumed by core, net, rw, uring_cmd, memmap, and registration paths.
