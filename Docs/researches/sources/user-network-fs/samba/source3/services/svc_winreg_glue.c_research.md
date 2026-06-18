# sources/user-network-fs/samba/source3/services/svc_winreg_glue.c

Purpose: glue layer between the service-control subsystem and the registry backend under `HKLM\SYSTEM\CurrentControlSet\Services`.

Important functions and APIs: `svcctl_gen_service_sd()` builds a default self-relative security descriptor with ACEs for World read, Power Users execute, Server Operators full, and Administrators full. `svcctl_get_secdesc()` opens `<Services>\<name>\Security`, queries value `Security`, and falls back to the generated default descriptor if missing. `svcctl_set_secdesc()` opens the service key, creates the `Security` subkey, and writes the descriptor. `svcctl_get_string_value()` reads string values from a service key. `svcctl_lookup_dispname()` and `svcctl_lookup_description()` return registry `DisplayName`/`Description` or defaults.

Control flow: all registry operations go through internal winreg RPC helpers (`dcerpc_winreg_int_hklm_openkey`, `dcerpc_winreg_query_sd`, `dcerpc_winreg_CreateKey`, `dcerpc_winreg_set_sd`, `dcerpc_winreg_query_sz`). Error handling maps NTSTATUS transport failures to internal errors and propagates WERROR registry failures.

State and persistence: security descriptors and string metadata persist in the Samba registry TDB/hive backing HKLM. Temporary allocations use talloc stack frames; policy handles are closed when valid.

Dependencies and integration: depends on messaging/auth session context, generated winreg NDR client bindings, security descriptor helpers, global SIDs, and svcctl callers. It is the persistence path for service ACLs and display metadata exposed over service-control RPC.

Risks and test signals: missing close of `hive_hnd` may be handled by helper lifetime but should be reviewed with the winreg API contract. Registry path creation and descriptor serialization are security-sensitive. Strong test signals come from svcctl security descriptor get/set RPC tests and registry metadata lookups.
