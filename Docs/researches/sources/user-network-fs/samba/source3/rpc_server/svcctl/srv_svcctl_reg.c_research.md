# sources/user-network-fs/samba/source3/rpc_server/svcctl/srv_svcctl_reg.c

Purpose: Seeds the Samba registry with service-control-manager service keys under `SYSTEM\\CurrentControlSet\\Services`. It creates built-in and configured external service records with display names, image paths, descriptions, basic service values, and default service security descriptors.

Important APIs/functions: `svcctl_init_winreg()` opens HKLM services key as the system session, enumerates existing subkeys, and adds missing built-in/configured services via `svcctl_add_service()`. `svcctl_add_service()` creates the service key, writes `Start`, `Type`, `ErrorControl`, `ObjectName`, `DisplayName`, `ImagePath`, and `Description`, then creates a `Security` subkey and stores a generated service security descriptor. `read_init_file()` parses service script comments for `Description:`. `svcctl_get_common_service_dispname()` maps common Unix service names to friendlier display names.

Control flow and state: Persistent state is the registry backend reached through internal winreg RPC calls. Built-in service metadata is hardcoded; external service metadata comes from `lp_svcctl_list()` and optional init script descriptions under `${MODULESDIR}/${SVCCTL_SCRIPT_DIR}`. Temporary state lives under a stackframe and policy handles are closed on exit.

Dependencies and integration: Depends on service metadata/glue, generated winreg client stubs, internal winreg helpers, auth system session, registry backend DB, and Samba loadparm service list. It is invoked during SVCCTL server initialization before generated endpoint init.

Risks and test signals: There are suspicious skip-loop index uses comparing `subkeys[i]` instead of `subkeys[j]`, which can miss existing keys or read the wrong entry. Error handling must close policy handles and avoid partially initialized service keys. Test registry seeding on empty and pre-populated registries, built-in/external service lists, missing/unreadable init files, generated security descriptor presence, and idempotent repeated startup.
