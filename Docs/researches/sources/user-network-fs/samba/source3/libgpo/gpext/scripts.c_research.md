# sources/user-network-fs/samba/source3/libgpo/gpext/scripts.c

## Purpose

Implements the Group Policy Scripts extension. It reads `Scripts/scripts.ini` from changed GPOs and writes Startup, Shutdown, Logon, and Logoff script definitions into policy registry keys under `Software\Policies\Microsoft\Windows\System\Scripts`.

## Important APIs, Types, and Functions

`gpext_scripts_init` registers the extension. `scripts_get_reg_config` advertises extension registry metadata. `scripts_parse_ini_section` scans numbered `cmdline` and `parameters` entries and emits `Script`, `Parameters`, and zeroed `ExecTime` registry values. `generate_gp_registry_entry` builds `gp_registry_entry` records. `scripts_store_reg_gpovals` stores GPO identity metadata. `scripts_apply` recreates a section key and applies entries. `scripts_process_group_policy` drives processing.

## Control Flow

For each changed GPO, the callback resolves the cached path, opens `Scripts/scripts.ini`, then loops through the four script sections. A section scan starts at index `0` and stops when either the command or parameter key is missing. Each parsed script becomes three registry values. `scripts_apply` deletes the old section key, recreates it, stores DisplayName/FileSysPath/GPO-ID/GPOName/SOM-ID, then calls `reg_apply_registry_entry` for generated values.

## State and Persistence Behavior

The module has a static registration context. Persistent side effects are registry key deletion/recreation and policy value writes. Deleted GPOs are ignored. Apply failures inside a section are currently continued past with a FIXME about empty strings and `REG_QWORD`.

## Dependencies and Integration Points

Depends on libgpo INI parsing, registry helpers from `registry.h`, `reg_apply_registry_entry`, and the `gpext` ABI. Built as `gpext_scripts`.

## Risks and Test Signals

Risks include skipped cleanup for deleted GPOs, partial application because section write failures are ignored, and possible overwrites because `scripts_apply` starts its registry subkey count at zero for each call. Tests should cover missing sections, sparse numbering, empty parameters, multiple changed GPOs, registry replacement behavior, and extension registration metadata.
