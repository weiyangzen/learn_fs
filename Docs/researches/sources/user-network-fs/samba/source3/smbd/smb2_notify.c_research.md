# sources/user-network-fs/samba/source3/smbd/smb2_notify.c

Purpose: implements SMB2 CHANGE_NOTIFY on directory handles by bridging SMB2 requests into Samba's change-notify subsystem with immediate replies, queued async notifications, cancellation, and output marshalling.

Important APIs and types: `smbd_smb2_request_process_notify()` decodes the packet. `smbd_smb2_notify_send()` / `smbd_smb2_notify_recv()` wrap the operation. `struct smbd_smb2_notify_state` stores SMB2/fake SMB1 request state, queued-request flags, status, and output. `smbd_smb2_notify_reply()` is the notify callback. Destructors manage queued request cancellation and talloc parent recovery.

Control flow: the processor verifies body size `0x20`, output size against max-trans, credit charge, and fsp resolution. The send helper creates fake SMB1 state, rejects non-directory or wrong-connection fsp, creates `fsp->notify` if absent, replies immediately when changes are pending, or queues via `change_notify_add_request()`. Because that helper talloc-moves the SMB request, a destructor moves it back later. The notify callback maps zero-length OK replies to `NOTIFY_ENUM_DIR`, copies non-empty output, defers completion to the SMB2 event context, and completes or errors. The done callback returns the `0x08` response with output.

State and persistence: queued notify requests live in the change-notify subsystem attached to the fsp. This file tracks whether a request is queued and cancels it on state destruction or explicit cancel. No filesystem state is written.

Dependencies and integration: depends on SMB2 size/credit helpers, fake SMB1 glue, change-notify APIs, talloc destructors, tevent cancellation, and async profiling. It integrates with directory handles from SMB2 CREATE and backend notify implementations such as inotify.

Risks: ownership is subtle because queued notify moves `smbreq`; wrong destructor behavior can leak or use-after-free. `skip_reply` prevents late replies after cancellation. Zero-length OK becomes `NOTIFY_ENUM_DIR`. Completion filter is stored in a 64-bit variable but read with a 32-bit macro.

Test signals: cover `smb2.notify`, notify disabled, inotify-enabled notify, non-directory handles, max-trans/credit violations, immediate pending changes, queued delivery, zero-length enumeration status, cancellation, close while pending, and recursive watch.
