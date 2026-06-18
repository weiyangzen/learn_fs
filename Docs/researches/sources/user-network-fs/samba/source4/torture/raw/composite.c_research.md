# sources/user-network-fs/samba/source4/torture/raw/composite.c

Purpose: This file tests Samba libcli composite SMB helpers under parallel asynchronous load: save/load file, fetch file through a fresh connection, append ACL, and query filesystem object ID.

Important APIs, types, and functions: `loadfile_complete()` increments a shared completion counter. Tests exercise `smb_composite_savefile`, `smb_composite_loadfile_send/recv`, `smb_composite_fetchfile_send/recv`, `smb_composite_appendacl_send/recv`, `smb_composite_appendacl`, and `smb_composite_fsinfo_send/recv`. `torture_raw_composite()` registers four 1-SMB tests.

Control flow: Loadfile saves random data and launches 50 parallel load operations, polling tevent until all callbacks fire, then verifies size and bytes. Fetchfile saves random data, builds a connection description from torture settings and command-line credentials, launches `torture_numops` fetches, and verifies returned data. Appendacl creates 50 empty files, records original ACLs, builds one test ACE, launches parallel append operations, and compares final DACLs with expected ACLs. Fsinfo launches parallel object-ID queries and prints returned GUIDs.

State and persistence behavior: It creates `\\composite`, random test files, and ACL changes, then calls `smb_raw_exit()` and deletes the tree for each test wrapper. It also uses current command-line credentials and share settings to make additional connections.

Dependencies and integration points: Dependencies include tevent, libcli composite APIs, raw SMB, security descriptor helpers, command-line credential access, resolver context, gensec settings, and `torture_numops`.

Risks: These tests are concurrency-sensitive. They assume callbacks always fire; if an async operation stalls the loop waits indefinitely. Fetch/fsinfo depend on host/share settings and credential validity. Appendacl assumes ACL support and stable ACE ordering.

Test signals: Passing shows composite helper APIs preserve data integrity and ACL semantics under parallel use and that async completion, connection setup, and object-ID query paths remain functional.
