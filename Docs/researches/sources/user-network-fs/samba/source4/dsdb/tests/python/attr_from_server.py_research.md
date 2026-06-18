# sources/user-network-fs/samba/source4/dsdb/tests/python/attr_from_server.py

Purpose: this test covers a corner case for the mandatory `fromServer` Object(DS-DN) attribute on `nTDSConnection`: an existing valid link can become dangling after the referenced server is deleted and tombstone-expunged, and unrelated modifications to the connection should still succeed.

Important APIs/types/functions: `FromServerAttrTest` connects to a local SamDB path with `samba.tests.connect_samdb()`. Helpers `set_attribute()` and `get_object_guid()` wrap LDB modify/search work. `test_dangling_server_attr()` creates a temporary server, an `nTDSDSA` object using `relax:0`, an `nTDSConnection` under the test DC from `os.environ["SERVER"]`, validates bad replacement failure, deletes the temporary server, expunges tombstones via `garbage_collect_tombstones()`, and modifies `description` again.

Control flow: the script accepts a local LDB filepath rather than a host URL because it needs system-only object creation. It builds configuration/site/server DNs from `DEFAULTSITE`, then executes one targeted test under `TestProgram`.

State and persistence behavior: the connection object is registered with `addCleanup(self.ldb.delete, ntds_conn)`, but the temporary server is deleted during the scenario. Tombstone garbage collection mutates persistent database state and intentionally removes the deleted server object.

Dependencies and integration points: integrates with Samba provision constants, `misc.GUID`, local SamDB internals, `relax` control, `show_deleted`, tombstone garbage collection, and the `SERVER` environment variable.

Risks: this must run against a local database, not a remote LDAP URL. It depends on wall-clock `time.sleep(1)` and manual tombstone lifetime `0`. Missing `SERVER` or unexpected site topology breaks DN construction. The test deliberately creates an inconsistent link state.

Test signals: it asserts valid modification before deletion, `ERR_CONSTRAINT_VIOLATION` for setting `fromServer` to a never-existing DN, visibility then expunging of the deleted server by GUID, and successful unrelated modification after the link target is gone.
