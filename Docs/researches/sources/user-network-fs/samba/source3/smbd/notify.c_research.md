# sources/user-network-fs/samba/source3/smbd/notify.c

## Purpose
`notify.c` implements SMB change-notify request tracking and delivery inside smbd. It stores per-fsp notify subscriptions, queues filesystem change events, marshals `FILE_NOTIFY_INFORMATION` replies, cancels pending requests by MID/fid/request, reregisters watches after notifyd restarts, enforces optional ChangeNotify privilege visibility rules, and triggers backend notifications for changed filenames.

## Important APIs, Types, And Functions
Key local types are `notify_change_event`, `notify_change_buf`, `notify_change_request`, and `notify_mid_map`. Public APIs include `change_notify_fsp_has_changes()`, `change_notify_reply()`, `notify_callback()`, `change_notify_create()`, `change_notify_add_request()`, `remove_pending_change_notify_requests_by_mid()`, `smbd_notify_cancel_by_smbreq()`, `smbd_notify_cancel_deleted()`, `smbd_notifyd_restarted()`, `remove_pending_change_notify_requests_by_fid()`, `notify_fname()`, `notify_filter_string()`, and `sys_notify_context_create()`.

Internal helpers include `notify_marshall_changes()` for sorted/coalesced NDR encoding, `change_notify_remove_request()` for unlinking both fsp request and MID map lists, `smbd_notify_cancel_by_map()` for choosing cancellation status in SMB2 cleanup cases, `user_can_stat_name_under_fsp()` for access-filtering notification visibility, and `notify_fsp()` for queueing and replying to a notified fsp.

## Control Flow
`change_notify_create()` validates list access on the directory fsp, allocates `fsp->notify`, stores filters and maximum response size, computes the full path, and registers with notifyd when filters are nonzero. `change_notify_add_request()` moves the incoming SMB request under a new notify request object, appends it to the fsp queue, and adds a MID lookup map to `sconn->notify_mid_maps`.

Backend events enter via `notify_callback()`, which finds the target fsp in `sconn->files` and calls `notify_fsp()`. `notify_fsp()` optionally enforces ChangeNotify privilege semantics, rejects hidden events, caps queued events at 1000 or converts backend drop indications (`name == NULL`) into catch-all state, stores the event with slash-to-backslash conversion, holds `OLD_NAME` rename halves until the paired event arrives, and replies to the first waiting request when deliverable. `change_notify_reply()` clamps to the server buffer limit, marshals sorted and coalesced changes, sends an empty response if the client buffer is too small or catch-all state is present, then clears queued changes.

Cancellation flows locate a MID map or request pointer, compute `CANCELLED` versus `NOTIFY_CLEANUP` for SMB2 session/tcon cleanup, send a completion, and remove request/map state. Delete notifications and notifyd restarts are delivered through messaging callbacks that walk all fsps.

## State And Persistence
State is per-process memory: `fsp->notify` buffers, queued changes, pending request lists, and `sconn->notify_mid_maps`. Notify registrations live in `sconn->notify_ctx` and are recreated after notifyd restarts. No persistent storage is owned by this file. Event names are talloc-owned under the changes array, and the request object owns the moved `smb_request`.

## Dependencies And Integration Points
This file integrates with notifyd through `notify_add()`, `notify_init()`, `notify_trigger()`, and callback private data; with file lifecycle through `fsp_unbind_smb()` and `files_forall()`; with SMB1/SMB2 request reply functions supplied by callers; with SMB2 session/tcon cleanup state from `globals.h`; with directory lease break handling through `contend_dirleases()`; and with security/access checks through privilege tests, user switching, `synthetic_pathref()`, and `smbd_check_access_rights_fsp()`.

## Risks
Risks include request leaks in cancellation paths, missed removal from either the fsp list or MID map list, incorrect SMB2 cleanup status, event disclosure without adequate traverse/list rights, queue growth or catch-all behavior under event storms, rename old/new event pairing, buffer-size truncation semantics, and stale registrations after notifyd restart. `notify_fsp()` currently replies only to the first waiting request, so multi-request behavior must match SMB semantics.

## Test Signals
Tests should cover access denied on notify creation, duplicate notify create rejection, zero filters, recursive versus nonrecursive filters, request queue ordering, MID cancellation, SMB2 session/tcon cleanup cancellation status, delete-pending cancellation by file id, notifyd restart reregistration, marshalling order and duplicate coalescing, max buffer too small, catch-all state, more than 1000 queued events, rename old/new pairing, slash conversion, ChangeNotify privilege enabled/disabled, traverse/list failures hiding events, dirlease break actions, filter string formatting, and sys notify context allocation failure.
