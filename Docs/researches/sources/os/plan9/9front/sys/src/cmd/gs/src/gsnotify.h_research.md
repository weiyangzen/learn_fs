# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsnotify.h

Public notification-list interface.

Key definitions:
- `gs_notify_proc_t`: callback receiving `proc_data` and `event_data`.
- `gs_notify_registration_t`: callback, callback data, next pointer.
- `gs_notify_list_t`: allocator pointer and first registration.
- GC descriptor macros for registration and list structures.

Key declarations:
- `gs_notify_init`
- `gs_notify_register`
- `gs_notify_unregister`
- `gs_notify_unregister_calling`
- `gs_notify_all`
- `gs_notify_release`

Research notes:
- Comments specify that clients must unregister when finalized, and notifying object finalization uses `event_data = NULL`.
