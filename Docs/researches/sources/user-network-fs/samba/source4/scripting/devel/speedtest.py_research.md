<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/speedtest.py -->
# sources/user-network-fs/samba/source4/scripting/devel/speedtest.py

Purpose: Samba Python subunit performance test for bulk user creation/deletion and ACL-filtered LDAP searches.

Important APIs/types/functions: `SpeedTest`, `SpeedTestAddDel`, `AclSearchSpeedTest`, `create_user`, `create_bundle`, `remove_bundle`, `run_bundle`, `run_search_bundle`, `SamDB`, `sd_utils.SDUtils`, `delete_force`, and `TestProgram`.

Control flow: requires a host, builds sealed credentials, opens `SamDB` with `paged_searches`, then subunit discovers test methods. Add/delete tests remove stale users and time three attempts for 10, 100, and 1000 object bundles. ACL search tests create a restricted user, add ACEs to users or container, search as admin or restricted user, average three search timings, and clean up.

State and persistence behavior: mutates the target directory by creating and deleting `speedtestuserN` and `acltestuser` objects and modifying DACLs. Cleanup is attempted through test teardown and delete helpers.

Dependencies and integration points: integrates with Samba test framework, LDB over LDAP, security descriptors, and credential/gensec sealing.

Risks: performance tests are invasive and can leave objects after interruption. The 10000-user test is disabled because it is slow. Global `ldb` is initialized after class definitions but before `TestProgram`, so import ordering matters.

Test signals: subunit test results plus printed timing averages for ADD, DEL, and SEARCH operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/speedtest.py -->
