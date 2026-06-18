# sources/user-network-fs/samba/source3/libsmb/errormap.c

Purpose: this file is a compact translation layer between legacy SMB/DOS error tuples, winbind `wbcErr` values, and Samba `NTSTATUS`. It is used where older protocol responses or winbind APIs must be normalized before the higher libsmbclient layers convert status to Unix `errno`.

Important APIs and state: `dos_to_ntstatus(uint8_t eclass, uint32_t ecode)` linearly searches the static `dos_to_ntstatus_map[]`, returning `NT_STATUS_OK` for DOS class zero and `NT_STATUS_UNSUCCESSFUL` for unknown mappings. `map_nt_error_from_wbcErr(wbcErr wbc_err)` similarly searches `wbcErr_ntstatus_map[]`. Both tables are process-static immutable data and have no persistence or allocation behavior.

Control flow and dependencies: callers supply protocol-originated error class/code pairs or winbind return codes; the file depends on `includes.h` for `ERRDOS`, `ERRSRV`, `ERRHRD`, `NT_STATUS_*`, `STATUS_*`, `ARRAY_SIZE`, and `wbcErr`. There is no dynamic dispatch; correctness is entirely table coverage and exact equality.

Integration points: directory listing callbacks use `map_nt_error_from_unix()` elsewhere, while this file gives the reverse side for DOS and winbind sources. It feeds the common Samba status/errno conversion path used by libsmbclient operations.

Risks: unmapped DOS codes collapse to `NT_STATUS_UNSUCCESSFUL`, which can lose useful user-facing detail. The table includes raw literal status values, so future protocol changes need careful review. Test signals should include known DOS class/code pairs, unknown pairs, class zero, every `wbcErr_ntstatus_map[]` entry, and one unmapped winbind value.
