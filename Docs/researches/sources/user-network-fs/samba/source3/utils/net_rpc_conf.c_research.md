# sources/user-network-fs/samba/source3/utils/net_rpc_conf.c

## Purpose

`net_rpc_conf.c` implements `net rpc conf`, a remote management interface for Samba configuration stored in the registry backend. Its command surface reads, imports, creates, edits, and deletes share definitions under the fixed Winreg path `HKLM\Software\Samba\smbconf`, printing results in an smb.conf-like format. It is explicitly designed for local or remote RPC interaction with registry-backed configuration, not for editing the local text `smb.conf` directly.

## Important APIs, Types, and Functions

The file is built around Winreg RPC, `struct smbconf_service`, and Samba's `net_context` command framework. `rpc_conf_open_conf()` opens `HKLM` and the `Software\Samba\smbconf` key with a requested access mask. `rpc_conf_get_share()` enumerates values from a share subkey into `struct smbconf_service`, converting registry `includes` multi-string values back into repeated `include` parameters. `rpc_conf_set_share()` performs the inverse conversion, creating a share key and storing normal parameters with `dcerpc_winreg_set_sz()` while folding repeated `include` parameters into a single `includes` `REG_MULTI_SZ`. `rpc_conf_del_value()` opens a share subkey and deletes a named value, treating `WERR_FILE_NOT_FOUND` as non-fatal for delete operations.

The command internals are `rpc_conf_listshares_internal()`, `rpc_conf_list_internal()`, `rpc_conf_showshare_internal()`, `rpc_conf_addshare_internal()`, `rpc_conf_delshare_internal()`, `rpc_conf_drop_internal()`, `rpc_conf_import_internal()`, `rpc_conf_getparm_internal()`, `rpc_conf_setparm_internal()`, `rpc_conf_delparm_internal()`, and the `getincludes`/`setincludes`/`delincludes` variants. The exported `net_rpc_conf()` builds the `functable` used by `net_run_function()`, while each command wrapper calls `run_rpc_command()` with `ndr_table_winreg`.

## Control Flow

All mutating and read operations follow the same shape: validate `argc` and `c->display_usage`, open a Winreg pipe via `run_rpc_command()`, open the smbconf registry root, perform the specific key/value operation, translate `WERROR` to `NTSTATUS` on failure, and close policy handles before freeing the talloc stack frame. Listing first enumerates share subkeys, then optionally retrieves each share with `rpc_conf_get_share()` and prints it through `rpc_conf_print_shares()`. `addshare` parses a small positional grammar for `writeable=`, `guest_ok=`, and optional comment, creates a new key, rejects already existing shares, and stores `path`, `read only`, `guest ok`, and `comment`.

`import` reads a text file through `smbconf_init("file:<filename>")`, optionally limits to one service, prints the parsed services in test mode, otherwise drops the remote smbconf registry tree and rewrites it from the parsed `smbconf_service` records. `setparm` creates or opens a share key, deletes any existing value when opened, validates the value with `net_conf_param_valid()`, and writes a new `REG_SZ`.

## State and Persistence

Persistent state is entirely remote registry state below `HKLM\Software\Samba\smbconf`. `drop` deletes and recreates the whole root, `import` performs a destructive replace before setting shares, and the parameter/include commands mutate individual registry values. There is no local persistent state beyond the input file read by `import`. Talloc stack frames contain transient service arrays, registry value strings, and policy handles.

## Dependencies and Integration Points

This file depends on generated Winreg RPC stubs, `rpc_client/cli_winreg.h`, `lib/smbconf`, `net_conf_util`, `loadparm`, and the common `net` RPC runner. It integrates with Samba's command tree via `net_rpc_conf()` and with the registry smbconf backend used by Samba's configuration system.

## Risks

`rpc_conf_import_internal()` drops the full remote configuration before writing imported shares, so partial failures can leave the remote smbconf backend empty or incomplete. Several create calls request `REG_KEY_READ` while subsequently setting values through the returned handle, which depends on server-side behavior and may be fragile. The import test-mode branch prints `services[i]` even when importing a single `servicename`, where `services` remains `NULL`; that path is a concrete crash risk. Input parsing for `addshare` checks only the first value character after `writeable=` and `guest_ok=`, so extra trailing text is ignored. Delete operations intentionally suppress missing values, which is convenient but can hide typos.

## Test Signals

Useful tests are command-level RPC integration tests against a temporary registry backend: list empty/non-empty config, add/show/del share round trips, `setparm` validation failures, include multi-string round trips, and destructive `import --test` versus real import. Regression coverage should include single-service import in test mode, failure injection after `drop`, and case-insensitive share lookup in `rpc_conf_get_share()`.
