# sources/user-network-fs/samba/source3/rpc_server/spoolss/srv_spoolss_util.c

Purpose: Implements spoolss helper wrappers that call Samba's internal winreg RPC client routines. The file centralizes creation of a local winreg binding handle and then forwards printer, driver, form, security descriptor, core-driver, and driver-package operations to `cli_winreg_spoolss` helpers.

Important APIs: `winreg_printer_binding_handle()` builds a loopback `127.0.0.1` tsocket address and calls `rpcint_binding_handle()` for `ndr_table_winreg`. The rest of the exported `*_internal()` functions all follow the same pattern: allocate a stackframe, obtain the winreg binding, call the corresponding `winreg_*` helper, free the temporary context, and return `WERROR`. Covered operations include printer create/update/get/delete-key/changeid, printer data get/set/enum/delete, driver get/list/add/delete, core driver get/add, driver package get/add/delete, printer security descriptor get/set, form enum/get/add/set/delete, and printer key enumeration.

Control flow and state: The helpers are synchronous wrappers. Persistent state lives in the registry backend reached through the winreg server, not in this file. Output data is allocated on the caller-provided `mem_ctx`; temporary binding objects live on `tmp_ctx`. Every failure to allocate or bind returns immediately with `WERR_NOT_ENOUGH_MEMORY` or the winreg connection error.

Dependencies and integration: Includes `rpc_server/rpc_ncacn_np.h`, tsocket, generated spoolss/winreg NDR headers, `srv_spoolss_util.h`, and `rpc_client/cli_winreg_spoolss.h`. It bridges spoolss server code to the registry-backed printer database without duplicating registry path logic.

Risks and test signals: The repeated wrapper pattern is easy to regress by passing `tmp_ctx` where caller-owned output is required; output-owning helpers intentionally receive `mem_ctx`. Binding failures are logged at level 0 and surface as converted `WERROR`s. Test with printer add/update/delete, driver package install/remove, form operations, and printer ACL get/set while forcing winreg unavailable and low-memory paths.
