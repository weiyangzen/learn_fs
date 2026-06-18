<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawlpq.c -->
# sources/user-network-fs/samba/source4/libcli/raw/rawlpq.c

Purpose: `rawlpq.c` is a placeholder for raw SMB print queue (`SMBsplretq`) support. It declares the send/recv/sync shape for `union smb_lpq` but does not implement packet encoding or parsing.

Important APIs, types, and functions: The file contains `smb_raw_lpq_send`, `smb_raw_lpq_recv`, and `smb_raw_lpq`. `smb_raw_lpq_send` always returns `NULL`; `smb_raw_lpq_recv` always returns `NT_STATUS_NOT_IMPLEMENTED`; the sync wrapper simply calls both.

Control flow: There is no real protocol flow. Any caller of the sync function receives `NT_STATUS_NOT_IMPLEMENTED`. A caller using send directly gets no request object.

State and persistence behavior: No local or server state is touched. The `union smb_lpq` output queue fields defined in `interfaces.h` are never populated by this implementation.

Dependencies and integration points: It includes the raw umbrella header and prototype header to fit the raw module build. Integration is limited to code that might probe or attempt print queue operations; Samba print queue functionality, if present elsewhere, does not use this file as a working raw implementation.

Risks: The API exists but is nonfunctional, so callers may assume print queue support based on declarations and only fail at runtime. Because send returns `NULL`, generic sync patterns that destroy a request would map to unsuccessful statuses, but this recv explicitly returns not implemented. No SMB2 equivalent is handled here.

Test signals: A minimal test should assert `smb_raw_lpq` returns `NT_STATUS_NOT_IMPLEMENTED` and does not dereference the `NULL` request. Any future implementation needs tests for queue entry parsing, maxcount/startidx behavior, user string conversion, and print server interoperability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/raw/rawlpq.c -->
