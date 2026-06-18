# sources/user-network-fs/samba/source4/dsdb/samdb/ldb_modules/tests/test_unique_object_sids.c

Purpose: This cmocka file directly includes `../unique_object_sids.c` and validates the LDB module that forces unique-index checking for local-domain `objectSID` values. It ensures local object SIDs are flagged, foreign or missing SIDs pass through, and direct non-replicated `objectSID` modification is rejected.

Important APIs, types, and functions: The tests exercise `unique_object_sids_init`, `unique_object_sids_add`, `unique_object_sids_modify`, and helper behavior behind `message_contains_local_objectSID` and `flag_objectSID`. It mocks `ldb_next_request` to record `last_request` and uses `add_sid` to NDR-encode textual SIDs into `objectSID` values.

Control flow: `setup` creates an LDB context, installs `cache.domain_sid`, builds a two-module chain ending in an `eol` module, connects a TDB file, and initializes the module. Add tests build `ldb_build_add_req` requests with local, foreign, or absent `objectSID` values. Modify tests build `ldb_build_mod_req` requests and optionally attach `DSDB_CONTROL_REPLICATED_UPDATE_OID`. Assertions verify whether the original request or a copied request reached the next module and whether `LDB_FLAG_INTERNAL_FORCE_UNIQUE_INDEX` was set only on the copied `objectSID` element.

State and persistence behavior: Tests create and delete `duptest.ldb` and its lock file. The module private state stores the local domain SID discovered through `samdb_domain_sid`. `last_request` is global test state capturing the request passed down the module chain.

Dependencies and integration points: The file depends on Samba LDB modules, NDR SID marshalling, `dom_sid_in_domain`, DSDB replicated-update controls, and TDB-backed LDB setup. It is tightly coupled to the production module's request-copying behavior.

Risks: The production boundary is important: local `objectSID` uniqueness cannot be enforced by a plain unique index because foreign principals and replication-conflict records may duplicate SIDs. The tests also reveal a likely copy/paste issue in assertions for modify paths that inspect `last_request->op.add.message` and `request->op.add.message` after building modify requests; the underlying union layout may make this work in practice, but it is fragile test code.

Test signals: Passing tests show local-domain SIDs get `LDB_FLAG_INTERNAL_FORCE_UNIQUE_INDEX`, foreign and missing SIDs are untouched, original requests are not mutated when flags are added, replicated updates may modify local object SIDs, and ordinary local objectSID modifies fail with `LDB_ERR_UNWILLING_TO_PERFORM`.
