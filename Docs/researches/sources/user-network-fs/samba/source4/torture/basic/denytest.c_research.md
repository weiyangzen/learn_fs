# sources/user-network-fs/samba/source4/torture/basic/denytest.c

## Purpose
This file implements Samba torture coverage for classic SMB deny modes, NT CreateX share/access behavior, and security-descriptor-driven maximum allowed access. It is a behavioral oracle for compatibility-sensitive file-open semantics, including DOS deny modes, NT share modes, file versus directory opens, delete/share-delete rules, SACL-sensitive access bits, and privilege-dependent `SEC_FLAG_MAXIMUM_ALLOWED` outcomes.

## Important APIs, types, and functions
Key local helpers include `denystr()`, `openstr()`, `resultstr()`, `progress_bar()`, `map_bits()`, `bit_string()`, and `predict_share_conflict()`. The main exported torture entry points are `torture_denytest1()`, `torture_denytest2()`, `torture_denytest3()`, `torture_ntdenytest1()`, `torture_ntdenytest2()`, `torture_denydos_sharing()`, `torture_createx_sharemodes_file()`, `torture_createx_sharemodes_dir()`, `torture_createx_access()`, `torture_createx_access_exhaustive()`, and `torture_maximum_allowed()`. The file relies on `union smb_open`, `union smb_read`, `union smb_write`, `union smb_fileinfo`, `union smb_setfileinfo`, `struct createx_data`, and `struct security_descriptor`.

## Control flow
The first half is table-driven. `denytable1` and `denytable2` encode expected read/write results for combinations of `O_RDONLY`, `O_WRONLY`, `O_RDWR` with `DENY_DOS`, `DENY_ALL`, `DENY_WRITE`, `DENY_READ`, `DENY_NONE`, and `DENY_FCB`, split between single-connection and two-connection behavior and `.dat` versus `.exe` names. The deny tests create seed files, iterate the tables, open one or two handles, probe read/write success on the second handle, compare to the table, and clean up.

The NT deny path randomly generates share/access masks, opens via `RAW_OPEN_NTCREATEX`, probes read/write behavior, and compares the server result with `predict_share_conflict()`. CreateX coverage uses `createx_fill_file()` and `createx_fill_dir()` to parameterize opens, then calls `createx_test_file()` or `createx_test_dir()` to exercise read/write/execute or enumerate/create-child/traverse operations. Results are checked against `cxd_known` unless exhaustive output mode is enabled through `CREATEX_DATA`.

## State and persistence
The tests create and remove files such as `\denytest*.dat`, `\denytest*.exe`, `\ntdeny_*.dll`, `\torture_denydos.txt`, `\createx_dir`, and `torture_maximum_allowed`. `data_file_fd` is a process-global descriptor used only by exhaustive CreateX data capture. `torture_numops`, `torture_seed`, `torture_failures`, and settings such as `deny_fcb_support`, `deny_dos_support`, `sacl_support`, `showall`, and `progress` shape execution. Cleanup is mostly explicit through `smbcli_close()`, `smbcli_unlink()`, `smbcli_rmdir()`, and `smbcli_deltree()`.

## Dependencies and integration points
The file integrates with Samba's `libcli` raw SMB layer, security descriptor helpers, torture assertions/results, and the generated `cxd_known.h` baseline. It assumes a connected `smbcli_state` or pair of connections supplied by the torture harness. `torture_check_privilege()` and `sec_privilege_name()` make `torture_maximum_allowed()` dependent on server-side privilege configuration.

## Risks
The dense static deny tables and `cxd_known` baselines are brittle by design: a server compatibility change may require updating expected data rather than code. Exhaustive CreateX access can be very expensive, especially when `CREATEX_DATA` is set. Some tests skip SACL paths based on settings, so coverage can silently narrow. Several cleanup paths continue after failed opens and may attempt closes on invalid fnums, which is normal for this torture style but can obscure the first failure.

## Test signals
Strong signals are mismatches between observed `A_0`, `A_R`, `A_W`, `A_RW`, `A_X` and expected table or predicted share-conflict results, unexpected `NT_STATUS_SHARING_VIOLATION`, `NT_STATUS_ACCESS_DENIED`, `NT_STATUS_PRIVILEGE_NOT_HELD`, or failure to preserve DENY_DOS shared-handle file-position semantics. For CreateX, unknown result tuples printed in initializer syntax indicate new or divergent server behavior.
