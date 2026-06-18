# File Research: sources/os/linux/linux/fs/notify/fanotify/fanotify.h

## Role

This header defines fanotify's private event, file-handle, name, permission, mount-event, and mark structures plus compact inline helpers used by fanotify implementation files.

It sits above the generic fsnotify backend and translates between generic `struct fsnotify_event` / `struct fsnotify_mark` objects and fanotify-specific payloads.

## File Handle And Name Payloads

`struct fanotify_fh` is a fixed-size file-handle header with type, length, flags, and alignment padding. Small handles are stored inline; larger handles use `FANOTIFY_FH_FLAG_EXT_BUF` and an aligned external buffer pointer.

`struct fanotify_info` stores variable-length directory file handle, optional second directory file handle, optional child/object file handle, and one or two names in one packed buffer. The macros compute ordered offsets for:

- old directory handle
- new directory handle for rename
- object/file handle
- first name
- second name for rename

The setter/copy helpers intentionally enforce write order so offsets remain valid.

## Event Types

`enum fanotify_event_type` distinguishes fixed FID events, variable FID/name events, path events, permission path events, overflow events, filesystem error events, and mount events.

`struct fanotify_event` embeds the generic `fsnotify_event`, a merge-hash list node, event mask, compact type/hash bitfields, and the reporting pid.

Concrete event wrappers include:

- `fanotify_fid_event` for fsid plus inline object file handle.
- `fanotify_name_event` for fsid plus variable `fanotify_info`.
- `fanotify_error_event` for filesystem error code/count plus fsid and object handle.
- `fanotify_path_event` for path-based notification.
- `fanotify_mnt_event` for mount namespace attach/detach reporting.
- `fanotify_perm_event` for permission/pre-content events awaiting userspace response.

## Permission Events

Permission events track a path, optional file range, userspace response, state machine, watchdog count, reported fd, receiver pid, and optional audit-rule response info.

The state values are `INIT`, `REPORTED`, `ANSWERED`, and `CANCELED`.

## Mark Helpers

`struct fanotify_mark` wraps a generic fsnotify mark and caches fsid data. Helpers translate internal mark flags back to fanotify user flags, compare fsids, and extract custom errno values from permission responses.

## Design Notes

The header keeps payload layout logic close to the structures. Most helpers are small, inline, and type-discriminating, which keeps the larger fanotify read/write/mark code from open-coding buffer offsets and container conversions.
