# sources/user-network-fs/samba/source3/libgpo/gpext/registry.c

## Purpose

Implements Samba source3's Group Policy registry extension. It finds each changed GPO's cached `Registry.pol`, parses the Windows `PReg` policy format, converts entries to `gp_registry_entry`, and applies them to the registry root supplied by the GPO engine.

## Important APIs, Types, and Functions

`gpext_registry_init` registers `registry_methods` for `GP_EXT_GUID_REGISTRY`. `reg_parse_value` maps policy value-name conventions to `enum gp_reg_action`, including add-key, add-value, delete-all-values, delete-value, and secure-key set. `gp_reg_entry_from_file_entry` converts generated NDR `preg_entry` records into Samba registry-policy entries. `reg_parse_registry` loads and validates `Registry.pol`; `reg_apply_registry` calls `reg_apply_registry_entry`; `registry_process_group_policy` is the extension callback.

## Control Flow

The callback ignores deleted GPOs, iterates `changed_gpo_list`, resolves a cache path with `gpo_get_unix_path`, loads `Registry.pol` through `gp_find_file` and `file_load`, parses it with `ndr_pull_preg_file`, validates `PReg` signature and version `1`, converts every entry, optionally dumps them, and applies them sequentially. The first parse or apply failure aborts processing and returns an NTSTATUS.

## State and Persistence Behavior

Module state is a static talloc registration context. Runtime arrays and blobs are talloc-scoped. Persistent behavior is registry mutation through `reg_apply_registry_entry`; it also reads cached GPO files under `GPO_CACHE_DIR`. Unsupported policy directives such as `**DeleteValues`, `**DeleteKeys`, and `**SecureKey=0` call `smb_panic`.

## Dependencies and Integration Points

Depends on libgpo file discovery, generated `ndr_preg`, registry helper types from `registry.h`, and the `gpext` registration ABI. Built as `gpext_registry` with `NDR_PREG` dependency in `wscript_build`.

## Risks and Test Signals

Risks include panic on unsupported special actions, deleted-GPO cleanup not implemented, and some conversion failures collapsing to `NT_STATUS_NO_MEMORY`. Tests should cover malformed policy files, wrong signatures/versions, add/delete actions, secure-key policies, verbose NDR dump paths, and registry write failure propagation.
