# sources/user-network-fs/samba/source3/utils/net_rpc_registry.c

## Purpose

`net_rpc_registry.c` implements `net rpc registry`, a remote Winreg management command family plus local registry hive file utilities. It can enumerate, create, delete, get, set, save, export, import, dump, and copy registry data, bridging Samba's command framework, generated Winreg RPC bindings, `.reg` formatting/parsing, and local `regfio` hive files.

## Important APIs, Types, and Functions

`dcerpc_winreg_Connect()` maps hive IDs to the corresponding Winreg open call. `reg_hive_key()` parses strings such as `HKLM\Software\Samba` or `HKEY_LOCAL_MACHINE\...` into a hive constant and relative key path using `split_hive_key()`. `registry_openkey()` opens the hive and requested subkey. `registry_enumkeys()`, `registry_enumvalues()`, and `registry_enumvalues2()` query key metadata, allocate buffers sized from `QueryInfoKey`, and enumerate subkeys or values into either `struct registry_value` or `struct regval_blob` representations.

Command internals implement remote set/delete/get value, create/delete key, enumerate, save, get security descriptor, export, and import. Local file helpers `dump_values()`, `dump_registry_tree()`, and `write_registry_tree()` use `regfio` to inspect or clone registry hive files. `registry_export()` recursively writes remote registry data through `struct reg_format`. Import is callback-driven through `struct import_ctx` and `reg_parse_file()`, with callbacks creating/deleting keys and values through Winreg.

## Control Flow

Remote commands parse arguments in their wrapper or internal function, open a Winreg pipe with `run_rpc_command(..., &ndr_table_winreg, ...)`, open the target hive/key, perform the operation, print formatted results, close handles, and return an `NTSTATUS`. `getvalue` performs the standard two-step `QueryValue`: first ask for required buffer size, then allocate and query the actual data. `enumerate` prints subkeys followed by values. `save` asks the remote server to save a registry key to a server-side file. `export` recursively opens subkeys, formats values, and writes a local `.reg` style file. `import` parses a local `.reg` file and applies each create/delete/set operation remotely.

The local `dump` and `copy` commands do not use RPC: they open hive files through `regfio_open()`, traverse the in-file tree, print values, or write a new hive file with copied subkey and value containers.

## State and Persistence

Remote persistent state is the selected registry hive/key on the target server. Mutations include creating/deleting keys, setting/deleting values, importing `.reg` data, and server-side `SaveKey`. Local persistent state is created by `export` and local hive `copy`; `dump` is read-only. The import callback owns Winreg policy handles with talloc and closes them through the adapter.

## Dependencies and Integration Points

Dependencies include generated Winreg and security NDR, `net_registry_util` print helpers, `registry/regfio.h`, `registry/reg_format.h`, `registry/reg_import.h`, `util_reg`, `display_sec`, and Samba string conversion utilities. The file integrates with the top-level `net rpc registry` function table and with Samba's registry import/export infrastructure.

## Risks

`rpc_registry_setvalue_internal()` returns `NT_STATUS_OK` unconditionally after cleanup even when parsing or `registry_setvalue()` failed, which can hide errors from callers. The public usage advertises `multi_sz`, but setvalue implements only `dword` and `sz`. `import_delete_val()` checks `NT_STATUS` twice and never checks `WERROR` after `DeleteValue`, so remote delete failures can be missed. Some early returns skip closing already opened handles, for example after argument/type validation failure in setvalue. `registry_enumkeys()` and value enumeration set output counts to metadata counts even if enumeration stops early on `WERR_NO_MORE_ITEMS`. Local dump/copy traversals are recursive and can be expensive or fragile on malformed hive structures.

## Test Signals

Tests should cover hive parsing aliases, remote create/get/set/delete round trips for `REG_DWORD` and `REG_SZ`, raw versus formatted `getvalue`, recursive export/import of nested keys, security descriptor display, and local dump/copy with a fixture hive. Regression checks should assert non-OK return status on failed setvalue and deletevalue operations and verify advertised-but-unimplemented value types are reported consistently.
