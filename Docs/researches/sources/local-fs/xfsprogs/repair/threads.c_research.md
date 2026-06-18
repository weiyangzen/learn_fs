# File Research: sources/local-fs/xfsprogs/repair/threads.c

Thin wrapper around libfrog workqueues plus signal masking for worker threads.

Functions:
- `thread_init` blocks `SIGHUP` and `SIGALRM` delivery to threads so progress/reporting signals remain controlled.
- `create_work_queue` wraps `workqueue_create` and converts errors into fatal repair errors.
- `queue_work` wraps `workqueue_add`.
- `destroy_work_queue` terminates and destroys a queue, fatal on termination errors.

Used by AG scanning, slab sorting, and other parallel repair operations.
