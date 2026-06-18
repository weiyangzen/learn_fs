# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netfile.c

Purpose: integration tests for `NetFileEnum` and placeholder coverage for `NetFileGetInfo`. It verifies that file enumeration levels 2 and 3 can be called successfully on the target host.

Important APIs/functions: `test_netfileenum` calls `NetFileEnum` with NULL base path and user name, a requested level, unlimited preferred length, and a resume handle. `netapitest_file` invokes it for levels 2 and 3.

Control flow: the helper loops while status is `ERROR_MORE_DATA`, accepts success/more-data buffers, validates that the level is one of 2 or 3, iterates over `entries_read` without inspecting fields, frees the buffer, and returns final status. A disabled `#if 0` block sketches future `NetFileGetInfo` tests.

State and persistence: read-only enumeration of open remote files. No target-side state is changed. The test's usefulness depends on whether the server has open files at runtime.

Dependencies/integration: depends on public `NetFileEnum`, `FILE_INFO_2`, `FILE_INFO_3` declarations from `netapi.h` and shared helpers from `common.h`. It is run by `netapitest.c` after share tests.

Risks: because the loop does not inspect returned fields, it mostly catches transport/level regressions rather than data-mapping regressions. If `NetFileEnum` returns `ERROR_MORE_DATA` with zero entries, resume behavior may loop. The disabled get-info block references an unavailable `fid`, so meaningful file-detail testing still needs a setup phase that opens a file.

Test signals: stronger tests should open a known file over SMB, verify it appears in level 2/3 enumeration, close it with `NetFileClose` where appropriate, and then query `NetFileGetInfo` for its id.
