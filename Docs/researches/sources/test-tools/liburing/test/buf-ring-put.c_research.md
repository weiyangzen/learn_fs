# sources/test-tools/liburing/test/buf-ring-put.c

Purpose: tests lifetime safety of mmap-backed pbuf ring mappings after buffer groups are unregistered. Important APIs are `io_uring_register_buf_ring`, pbuf-ring `mmap`, `io_uring_unregister_buf_ring`, and `IOU_PBUF_RING_MMAP`.

Control flow: register and mmap ten buffer groups, unregister all groups, then repeatedly write to the still-mapped ring memory. State is the user mapping after kernel unregister; no I/O is submitted. Test signal is survival without crash plus successful register/unregister. Risk is use-after-free or mapping lifetime regression.
