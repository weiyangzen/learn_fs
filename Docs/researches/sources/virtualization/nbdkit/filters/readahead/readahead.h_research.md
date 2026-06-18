# File Research: sources/virtualization/nbdkit/filters/readahead/readahead.h

This internal header defines the background command queue shared by `readahead.c` and `bgthread.c`. Commands are either `CMD_QUIT` or `CMD_CACHE` and include the target `nbdkit_next`, offset, and count for cache requests.

It defines `struct bgthread_ctrl` with a vector-backed command queue, mutex, and condition variable, and declares `readahead_thread`. The header owns no policy; it only shares queue and thread-control types.
