# sources/user-network-fs/samba/source4/torture/rpc/dfs.c

## Purpose
`dfs.c` tests the NetDFS RPC interface through Samba's torture framework. It covers DFS manager version/init calls, DFS enumeration and info levels, standalone DFS root creation/removal, DC address getters/setters, and fault-tolerant table flushing.

## Important APIs, types, and functions
The suite registers against `ndr_table_netdfs`. Key helpers include `test_GetManagerVersion_opts`, `test_EnumLevel`, `test_EnumLevelEx`, `test_GetInfo`, `test_AddStdRoot`, `test_AddStdRootForced`, `test_RemoveStdRoot`, `test_FlushFtTable`, `test_GetDcAddress`, and `test_SetDcAddress`. Local provisioning helpers use `libnet_AddShare`, `libnet_DelShare`, `torture_open_connection_share`, `torture_setup_dir`, and `smbcli_deltree`. Constants define the temporary share, directory, and path: `smbtorture_dfs_share`, `\smbtorture_dfs_dir`, and `C:\smbtorture_dfs_dir`.

## Control flow
`torture_rpc_dfs()` creates one RPC tcase named `netdfs` and registers seven tests. Enumeration tests iterate fixed DFS levels and, for level 1 or 300 results, recursively call `GetInfo` or nested `EnumEx` on returned roots. The standalone root test starts with cleanup, creates a directory on `C$`, creates a share pointing to that directory, adds/removes a standard root, exercises forced root creation, then deletes the share and directory. Manager and FT-root helpers first query manager version so Windows Server 2003 unsupported responses can be accepted through `IS_DFS_VERSION_UNSUPPORTED_CALL_W2K3`.

## State and persistence behavior
This file creates real server-side state: a directory under `C$`, an SMB share, and a standalone DFS root. `test_cleanup_stdroot()` attempts pre-cleanup before setup, and `test_StdRoot()` deletes artifacts at the end. If an assertion aborts after provisioning, the share/root/directory can remain. `SetDcAddress` also writes DFS DC address information with TTL 1000. Enumeration and info tests are read-only.

## Dependencies and integration points
The module requires admin-capable credentials from `samba_cmdline_get_creds()`, a configured `host` torture setting, SMB access to `C$`, libnet share management support, and the generated DFS client stubs. It uses both RPC and SMB client paths, making it an integration test across NetDFS, SRVSVC/share management, and SMB filesystem access.

## Risks and edge cases
The test assumes Windows-like administrative shares and permissive credentials. Version handling is explicit for W2K3 unsupported paths but other server differences may still fail. The cleanup sequence is not transactional, so partial artifacts can remain. `EnumEx` level 300 can recurse into multiple roots and amplify environmental failures.

## Test signals
Assertions check NTSTATUS success, WERR success or accepted no-more-items/unsupported values, and successful cleanup calls. Important negative/compatibility signals are `WERR_NOT_SUPPORTED` for selected W2K3 manager-version paths and `WERR_NO_MORE_ITEMS` during DFS enum/info discovery.
