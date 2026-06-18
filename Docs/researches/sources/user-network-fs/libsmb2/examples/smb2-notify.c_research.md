# sources/user-network-fs/libsmb2/examples/smb2-notify.c

Purpose: This example exercises SMB2 change-notification support in synchronous and asynchronous modes.

Important APIs and types: It uses `smb2_notify_change`, `smb2_notify_change_async`, `free_smb2_file_notify_change_information`, `struct sync_cb_data`, `struct smb2_file_notify_change_information`, change notify flags, completion filters, `poll`, and `smb2_service`.

Control flow: The program parses a URL and optional `sync|async` mode, connects to the share, builds a watch-tree flag and broad completion filter, then either performs one synchronous notify request or starts an async notify request configured to execute repeatedly. Async mode waits until callback data indicates completion and checks callback status.

State and persistence behavior: It watches remote server state but does not mutate it. Runtime state includes notification callback data and returned notify structures, which are freed after printing.

Dependencies and integration points: It integrates public notify APIs with the internal sync callback pattern and the event loop. It includes `libsmb2-private.h` to reuse internal `sync_cb_data`, which makes it less purely public than most examples.

Risks: Async mode sets `execute_in_loop=1`, so completion behavior depends on the library marking the callback data finished despite reissuing notifications. A notify request may block indefinitely until server-side changes occur. The mode parser silently defaults to sync for unrecognized third arguments.

Test signals: Trigger file creation, deletion, rename, attribute, or security changes under the watched path and verify printed action/name data. Test both sync and async modes.
