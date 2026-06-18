# sources/user-network-fs/samba/source3/rpcclient/cmd_winreg.c

Purpose: this module adds basic WINREG inspection commands for HKLM keys and values.

Important APIs, types, and functions: handlers use `dcerpc_winreg_OpenHKLM`, `OpenKey`, `EnumKey`, `EnumValue_r`, `QueryMultipleValues`, `QueryMultipleValues2`, and `CloseKey`. `pull_winreg_Data` decodes NDR union data, and `display_winreg_data` prints `REG_DWORD`, `REG_SZ`, `REG_BINARY`, and `REG_MULTI_SZ`.

Control flow: commands open HKLM, optionally open a subkey, perform one-shot or iterative queries, handle `WERR_MORE_DATA` by retrying with larger buffers, display decoded values, and close handles when applicable.

State and persistence: all exported commands are read-only. Remote registry handles are transient and local state is talloc-scoped.

Dependencies and integration: depends on WINREG NDR stubs and misc NDR definitions, and is registered via `winreg_commands[]`.

Risks: `winreg_enumkey` only calls index 0 and uses the supplied string as the output buffer name, so it is not a complete recursive enumerator. Buffer pointer arithmetic in query-multiple display relies on server-provided offsets and lengths being valid after NDR unmarshalling.

Test signals: enumerate root and subkey values, query multiple value types, trigger `WERR_MORE_DATA`, check close-handle paths, and verify malformed key/value names return clean errors.
