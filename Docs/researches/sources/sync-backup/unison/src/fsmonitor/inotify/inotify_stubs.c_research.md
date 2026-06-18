# sources/sync-backup/unison/src/fsmonitor/inotify/inotify_stubs.c

Purpose: OCaml C bindings for Linux inotify used by Unison fsmonitor.

Important APIs: `stub_inotify_init`, `stub_inotify_ioctl_fionread`, `stub_inotify_add_watch`, `stub_inotify_rm_watch`, `stub_inotify_struct_size`, and `stub_inotify_convert`. Flag tables map OCaml flag-list indexes to inotify masks and returned event masks.

Control flow: initialization opens an inotify fd; add/remove watch convert OCaml flag lists and call inotify APIs; `FIONREAD` reports available bytes; conversion copies one `struct inotify_event` from an OCaml string and constructs an OCaml tuple `(wd, flags, cookie, len)`.

State/persistence: kernel inotify watch state exists behind the returned fd and watch descriptors. No file state is changed.

Dependencies/integration: Linux `<sys/inotify.h>`, OCaml unixsupport error mapping, and fsmonitor OCaml modules that read raw event buffers and names.

Risks: `inotify_init` lacks `IN_CLOEXEC`/nonblocking flags here. `stub_inotify_convert` assumes the buffer contains at least one full event header. `IN_EXCL_UNLINK` is treated as zero if unavailable, reducing behavior on old headers.

Test signals: fsmonitor tests should add/remove watches, trigger create/delete/modify/move events, verify flag decoding and cookie propagation, and handle queue overflow.
