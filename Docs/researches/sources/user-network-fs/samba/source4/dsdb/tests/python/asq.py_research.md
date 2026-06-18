# sources/user-network-fs/samba/source4/dsdb/tests/python/asq.py

Purpose: this correctness test validates LDAP Attribute Scoped Query (ASQ) control behavior, including combinations with paged results, server-side sort, and VLV.

Important APIs/types/functions: `ASQLDAPTest.setUp()` builds a random OU, twenty first-level groups, twenty second-level groups whose `member` values point to the first level, and one top group whose `member` values point to the second level. `test_asq()`, `test_asq_paged()`, and `test_asq_vlv()` assert that a base search with `controls=["asq:1:member"]` returns the referenced objects. `test_asq_vlv_paged()` expects `ERR_UNSUPPORTED_CRITICAL_EXTENSION` when ASQ, VLV, sort, and paged results are combined.

Control flow: the module parses host/credentials, creates a `samba.Ldb` connection in each test, force-deletes any stale OU, creates fixture entries, runs the control-specific search, and deletes the OU via tree delete in `tearDown()`.

State and persistence behavior: fixture state is isolated under a randomized OU and cleaned after each test. Only failed setup/teardown can leave state behind.

Dependencies and integration points: integrates with LDAP controls `asq`, `paged_results`, `server_sort`, and `vlv`, Samba's LDB wrapper, credential handling, and subunit runner. It checks behavior expected from Windows for the unsupported ASQ+VLV+paged combination.

Risks: ASQ transforms a base search into multi-entry output, so result counting and DN assertions are important. Random OU names reduce collisions but make failed leftovers harder to inspect. Imported symbols such as `ndr_unpack`, `Credentials`, and some LDB error constants are unused.

Test signals: tests assert exact result count, exclude the top DN, verify returned DNs are second-level member targets, validate nested members, and assert the unsupported-critical-extension error for the conflicting controls.
