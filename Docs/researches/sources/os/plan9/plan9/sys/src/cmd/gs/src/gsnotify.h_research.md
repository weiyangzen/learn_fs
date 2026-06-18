# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnotify.h

Declares Ghostscript notification machinery. A `gs_notify_registration_t` stores callback, callback data, and next pointer. `gs_notify_list_t` stores allocator and first registration.

The header documents that duplicate registrations are not detected, clients must unregister before finalization, and providers should notify clients on provider finalization with `event_data == NULL`. It also declares private/public GC descriptor macros and the full registration, unregistration, notification, and release API.
