# File Research: sources/local-fs/xfsprogs/repair/threads.h

Header for repair workqueue helpers.

Exports:
- `thread_init`
- `create_work_queue`
- `queue_work`
- `destroy_work_queue`

Includes `libfrog/workqueue.h`, exposing `struct workqueue` and `workqueue_func_t` to callers.
