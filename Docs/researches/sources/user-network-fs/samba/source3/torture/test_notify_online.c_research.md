# sources/user-network-fs/samba/source3/torture/test_notify_online.c

Purpose: This file tests that reading an offline file through SMB triggers a file attribute change notification indicating the file has become online or otherwise changed. It is driven by the external `test_filename` argument.

Important APIs/types/functions: `struct notify_online_state` tracks directory and file handles plus a `got_notify` flag. `notify_online_send()` opens the containing directory, starts `cli_notify_send()` for `FILE_NOTIFY_CHANGE_ATTRIBUTES`, opens the target file, reads one byte with `cli_read_andx_send()`, closes file and directory, and waits up to ten seconds. `notify_online_recv()` returns whether the expected notify was observed. Public entrypoint is `run_notify_online()`.

Control flow: `run_notify_online()` requires `test_filename`, splits it into directory and basename, opens a torture connection, and calls `notify_online()`. The async state machine starts the notify before reading the file. The notify callback checks for exactly one change with `NOTIFY_ACTION_MODIFIED` and matching filename, then marks success.

State/persistence behavior: The test does not create the target file; it operates on the supplied file path and changes server-side file state indirectly by reading. State includes one directory handle, one file handle, an outstanding notify request, and a ten-second wakeup before directory close.

Dependencies and integration points: It depends on SMB client async create/read/close/notify calls, tevent NTSTATUS polling, security masks, and the torture harness global `test_filename`. It integrates with offline-file/VFS behavior where reads should trigger online transition notifications.

Risks: Requires an appropriately configured offline file; running it on a normal file may not produce the notify. Filename splitting uses `/`, while SMB paths may be environment-dependent. The notify matching is strict about action count, action type, and name.

Test signals: Passing requires `notify_online()` to return OK and `got_notify` true. Diagnostics print the returned NTSTATUS and boolean flag.
