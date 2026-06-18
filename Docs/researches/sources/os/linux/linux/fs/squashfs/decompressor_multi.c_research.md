# File Research: sources/os/linux/linux/fs/squashfs/decompressor_multi.c

Implements dynamic multi-stream decompression.

It maintains a mutex-protected list of available decompressor streams and can grow up to `num_online_cpus() * 2`, or a mount-limited `max_thread_num`. A wait queue blocks callers when all streams are busy.

At least one stream is allocated during create so the filesystem can operate even if later dynamic allocations fail.

Each decompression borrows one stream, calls the selected compression wrapper, returns the stream to the list, and logs corruption-style failures.
