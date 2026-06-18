<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawnotify.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawnotify.c

Purpose: `rawnotify.c` implements SMB1 raw change notification through `NT_TRANSACT_NOTIFY_CHANGE` and provides a cancellation helper for pending requests.

Important APIs, types, and functions: The main functions are `smb_raw_changenotify_send`, `smb_raw_changenotify_recv`, and `smb_raw_ntcancel`. They operate on `union smb_notify`, `struct smb_nttrans`, `struct notify_changes`, `smbcli_blob_pull_string`, and tevent request cancellation.

Control flow: Send accepts only `RAW_NOTIFY_NTTRANS`, fills a four-word setup array with completion filter, file number, and recursive flag, sets `max_param` to the caller's buffer size, and sends an NT transaction. Receive gets NT transaction params, walks the returned notify records once to count entries while validating 4-byte `next` alignment, allocates the changes array, then walks again to extract action codes and Unicode names. `smb_raw_ntcancel` cancels the first lower-level subrequest if one exists.

State and persistence behavior: Change notify requests may remain pending on the server until a filesystem change, cancellation, or disconnect. Locally the returned changes array and names are allocated under `mem_ctx`. Cancellation mutates the tevent/request state but does not wait for a server response.

Dependencies and integration points: It depends on NT transaction helpers, raw string parsing, and tevent. Higher-level directory watch logic and torture notify tests use this path for SMB1. SMB2 notify has interface definitions but is not implemented in this file.

Risks: The counting loop validates alignment but only checks `nt.out.params.length - ofs > 12`; malformed lengths near boundaries can lead to zero changes or parse failures. In the second loop, `ofs += IVAL(...)` can leave `ofs` unchanged on a zero final record after the last iteration, which is fine only because the loop is count-bounded. Cancellation returning success when no subrequest exists may hide already-completed requests.

Test signals: Notify tests should cover recursive and nonrecursive watches, multiple returned changes, rename pairs, zero-change completions, malformed `next` offsets, cancellation of pending requests, and invalid level rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawnotify.c -->
