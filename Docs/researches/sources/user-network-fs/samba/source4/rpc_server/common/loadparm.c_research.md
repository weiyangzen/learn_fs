# sources/user-network-fs/samba/source4/rpc_server/common/loadparm.c

Purpose: builds the `dcerpc_server_info` structure from Samba loadparm configuration without forcing the parameter subsystem to depend on RPC server internals.

Important APIs and control flow: `_PUBLIC_ lpcfg_dcerpc_server_info()` allocates a zeroed `dcerpc_server_info`, references `lpcfg_workgroup()` as `domain_name`, and reads `server_info:version_major`, `version_minor`, and `version_build` with defaults `5`, `2`, and `3790`.

State and persistence: no writes. Values are derived from the active `loadparm_context` and returned as talloc-managed memory. The `domain_name` is a talloc reference to configuration-owned memory, not a duplicate.

Dependencies and integration: included by DNS server utilities to compose Windows-compatible DNS server version fields. The type comes from `rpc_server/common/common.h`; loadparm accessors come from `lib/param/param.h`.

Risks and test signals: no NULL check after `talloc_zero()`, so allocation failure would dereference NULL. Tests should cover default values, configured override values, and lifetime safety when the returned structure outlives temporary contexts. DNS server info tests should confirm the bit-packed version matches these fields.
