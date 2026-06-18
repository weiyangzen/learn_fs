# sources/user-network-fs/samba/source4/torture/raw/context.c

Purpose: This file tests SMB1 context isolation and lifetime behavior for sessions/VUIDs, tree connections/TIDs, process IDs/PIDs, and automatic handle closure.

Important APIs, types, and functions: It uses `smbcli_session_init()`, `smb_composite_sesssetup()`, `smb_composite_sesssetup_send/recv()`, `smbcli_tree_init()`, `smb_raw_tcon()`, `smb_tree_disconnect()`, `smb_raw_ulogoff()`, `smb_raw_exit()`, raw open/write/close, and torture settings. Tests are `test_session()`, `test_tree()`, `test_tree_ulogoff()`, `test_pid_exit_only_sees_open()`, `test_pid_2sess()`, and `test_pid_2tcon()`.

Control flow: Session testing creates secondary security contexts on one transport, validates VUID allocation/failure rules, tests anonymous/non-extended cases, opens a file with one VUID and verifies another VUID cannot use the handle, then logs off and confirms auto-close. It also creates 15 parallel session setups and logs each off. Tree testing creates a second TID, verifies bad device type handling, checks handle isolation by TID, and validates auto-close on tree disconnect. Tree-with-ulogoff demonstrates a TCON can survive a session logoff and be reused with another valid session before disconnect. PID tests show `SMBexit` only closes handles opened under the matching PID and matching VUID/TID scope.

State and persistence behavior: The tests create files under `\\rawcontext`, mutate client-side VUID/TID/PID fields deliberately, and rely on server-side logoff, tree disconnect, and exit to close handles. Cleanup deletes the base directory.

Dependencies and integration points: It depends on raw SMB1 stateful semantics, composite session setup, command-line credentials, GENSEC settings, SMB negotiation capabilities such as `CAP_EXTENDED_SECURITY`, and torture host/share/workgroup configuration.

Risks: These tests depend on subtle SMB1 compatibility behavior and mutate client objects directly. Extended-security and non-extended-security servers legitimately differ. A failure before restoring IDs or deleting the tree can affect the shared connection for following tests.

Test signals: Passing confirms VUID/TID/PID scoping, invalid-handle/error behavior, ulogoff/tdis/exit cleanup semantics, secondary session setup concurrency, and tree reuse semantics match expected SMB1 behavior.
