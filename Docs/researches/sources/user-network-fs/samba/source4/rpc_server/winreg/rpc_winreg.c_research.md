<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/winreg/rpc_winreg.c -->
# sources/user-network-fs/samba/source4/rpc_server/winreg/rpc_winreg.c

## Purpose

`rpc_winreg.c` implements the Samba AD DC `winreg` DCE/RPC endpoint. It maps generated `winreg` RPC operations onto Samba's registry library, exposing predefined hives, key/value enumeration, basic key/value mutation, and a version query over the `dcerpc_server` handle model.

## Important APIs, Types, and Functions

The file uses `enum handle_types` to distinguish registry key handles from unused value handles. `dcesrv_winreg_openhive()` opens the Samba registry with the caller's `auth_session_info` and returns a `dcesrv_handle` wrapping a predefined key. The `func_winreg_OpenHive()` macro creates handlers for HKCR, HKCU, HKLM, HKPD, HKU, HKCC, HKDD, HKPT, and HKPN. Core handlers include `dcesrv_winreg_CreateKey()`, `DeleteKey()`, `DeleteValue()`, `EnumKey()`, `EnumValue()`, `OpenKey()`, `QueryInfoKey()`, `QueryValue()`, `SetValue()`, and `GetVersion()`.

## Control Flow

Generated NDR server glue included from `ndr_winreg_s.c` dispatches each RPC to the matching static handler. Open-hive and open-key paths create or reference `dcesrv_handle` objects; later calls recover them with `DCESRV_PULL_HANDLE_FAULT`. Read paths query registry backends and populate RPC output buffers with UTF-16 byte counts. Write paths first check `security_session_user_level()` and only allow `SECURITY_SYSTEM` or `SECURITY_ADMINISTRATOR` for create, delete, flush, and set operations. Many advanced operations return `WERR_NOT_SUPPORTED`.

## State and Persistence Behavior

Per-client registry handles live under the DCE/RPC call or connection talloc context until closed or unlinked. Persistent mutations are delegated to registry functions such as `reg_key_add_name()`, `reg_key_del()`, `reg_del_value()`, `reg_val_set()`, and `reg_key_flush()`. The endpoint itself stores no global registry state.

## Dependencies and Integration Points

It depends on `rpc_server/dcerpc_server.h`, `lib/registry/registry.h`, generated `ndr_winreg` and security descriptor parsers, and session-security helpers. Build integration is through the `dcerpc_winreg` module in `source4/rpc_server/wscript_build`.

## Risks and Edge Cases

The implementation is intentionally incomplete: security descriptor get/set, load/save/restore, notifications, shutdown, multiple-value queries, and extended delete are unsupported. Buffer-size checks are hand-coded around UTF-16 length units, so off-by-one behavior is important for Windows compatibility. `DeleteKey()` unlinks the input handle after deletion, which can surprise callers expecting parent-handle survival. Access checks are broad user-level checks rather than per-key ACL enforcement in this layer.

## Test Signals

Useful tests include RPC open-hive/open-key/read-only calls as normal users, create/set/delete as administrators, enumeration with undersized buffers expecting `WERR_MORE_DATA`, default-value queries, unsupported-operation status checks, and registry persistence checks through a second client connection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/winreg/rpc_winreg.c -->
