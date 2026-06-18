# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify.h

## Summary
Internal fanotify header defining event layouts, file-handle storage, name/fid record packing, permission-event state, mark metadata, and helper accessors used by fanotify event production and userspace copying.

## Main Types
- `struct fanotify_fh`: compact file-handle header with inline or external buffer support.
- `struct fanotify_info`: variable-length layout for old/new directory fids, child fid, and names.
- `struct fanotify_event` plus concrete event types: fid, name, path, permission path, overflow, fs-error, and mount events.
- `struct fanotify_perm_event`: permission/pre-content event state, fd, response, optional range, and audit-rule response info.
- `struct fanotify_mark`: fsnotify mark extension carrying cached fsid.

## Important Details
`fanotify_info` has strict append order: dir fh, second dir fh, file fh, first name, second name. Event type bits share storage with a merge hash. Error events always report an object fh even when invalid. Permission events are not hash-merged. Mark user flags translate internal fsnotify mark flags back to fanotify ABI flags.

## Risks
The variable record offsets and inline/external fh handling are ABI-sensitive because `fanotify_user.c` copies these structures into userspace info records. The ordered setters rely on callers building `fanotify_info` in exactly the documented sequence. Permission-event state transitions must match the read/write/release paths in `fanotify_user.c`.
