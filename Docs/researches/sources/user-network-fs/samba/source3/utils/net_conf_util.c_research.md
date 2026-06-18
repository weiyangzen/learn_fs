# sources/user-network-fs/samba/source3/utils/net_conf_util.c

Purpose: supplies shared parameter validation for `net conf` and `net rpc conf` writes.

Important APIs/types/functions: `net_conf_param_valid(service, param, valstr)` validates parameter name, registry backend allowance, global/service placement, and value parseability.

Control flow: checks `lp_parameter_is_valid()`, `smbconf_reg_parameter_is_valid()`, rejects global parameters outside `GLOBAL_NAME`, and calls `lp_canonicalize_parameter_with_value()` to validate the value.

State and persistence: no writes; it gates later smbconf persistence.

Dependencies/integration: depends on loadparm metadata, registry smbconf validation, and `GLOBAL_NAME`. Called by `net_conf_setparm()`.

Risks: `strequal(service, GLOBAL_NAME)` must be safe for callers that use NULL service names. Canonicalized output is not stored; validation succeeds but caller still writes original value spelling.

Test signals: invalid name; registry-disallowed parameter; global-only parameter in share; invalid value; global/empty service behavior.
