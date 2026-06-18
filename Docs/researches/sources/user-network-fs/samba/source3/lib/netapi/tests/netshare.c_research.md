# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netshare.c

Purpose: destructive integration tests for share NetAPI operations. It creates a test share, enumerates it, queries multiple levels, changes its comment, verifies the change, and deletes it.

Important APIs/functions: `test_netshareenum` loops over `NetShareEnum` levels 0, 1, and 2 and searches for a share name. `netapitest_share` exercises `NetShareAdd` levels 502 and 2, `NetShareDel`, `NetShareGetInfo` levels 0/1/2/501/1005, and `NetShareSetInfo` level 1004.

Control flow: the test deletes `torture_test_share`, tries adding level 502 with path `c:\`, deletes it, adds level 2, enumerates levels 0-2, queries supported get levels while tolerating 124, sets a comment through level 1004, fetches level 501, compares the returned remark, deletes the share, and verifies get-info fails.

State and persistence: mutates target share configuration. The path is Windows-style `c:\`, so the target environment must accept or map it. Output buffers are mostly freed in enum helper, but some get-info buffers are not freed in the main routine.

Dependencies/integration: depends on public share structs and prototypes plus shared test macros. It requires privileges to add/delete shares on the target and a server implementation that accepts the chosen path.

Risks: fixed share name and path make parallel or non-Windows-like test environments fragile. The test uses level 501 after setting level 1004 to verify remarks, matching implementation mapping, but does not validate DFS flags or security descriptors. Failure before deletion can leave a share behind. The implementation risk in `NetShareEnum_r` for counter selection should be caught by this test under sanitizers.

Test signals: run against isolated targets with unique names, validate level 2 fields, add security descriptor round-trip coverage for 502 where supported, free all buffers, and inject add/set/delete failures to confirm cleanup.
