# sources/user-network-fs/samba/source3/torture/test_nttrans_create.c

Purpose: This file tests NT transaction create with an explicit security descriptor, specifically that a file created without `WRITE_DAC` for Everyone subsequently denies an open requesting `WRITE_DAC_ACCESS`.

Important APIs/types/functions: The public entrypoint is `run_nttrans_create()`. It builds a `security_ace`, `security_acl`, owner SID, and self-relative `security_descriptor` via `make_sec_desc()`. It uses `cli_nttrans_create()`, `cli_query_secdesc()`, `cli_ntcreate()`, and `cli_nt_delete_on_close()`.

Control flow: The test opens a torture SMB connection, constructs an ACL granting `SEC_RIGHTS_FILE_ALL` except `SEC_STD_WRITE_DAC` to `global_sid_World`, creates `transtest` through `cli_nttrans_create()` with that descriptor, queries the security descriptor for diagnostics, then attempts a normal `cli_ntcreate()` asking for `WRITE_DAC_ACCESS`. It sets delete-on-close on the original handle and succeeds only if the second open returns `NT_STATUS_ACCESS_DENIED`.

State/persistence behavior: The remote file `transtest` is created and then marked delete-on-close through its original handle. Security descriptor state is persisted to the server long enough to test access checks.

Dependencies and integration points: It depends on Samba SMB client create APIs, security descriptor construction helpers, SID parsing, ACL constants, and torture connection helpers. It validates the server path that accepts security descriptors in NT_TRANSACT_CREATE.

Risks: Access-check behavior depends on server security model and share permissions. If the descriptor is not applied, inherited permissions may allow `WRITE_DAC`. The failure message for the second create prints `status` rather than `status2`, which can obscure diagnostics.

Test signals: Passing requires NT transaction create OK, delete-on-close OK, and the `WRITE_DAC_ACCESS` open to return exactly `NT_STATUS_ACCESS_DENIED`.
