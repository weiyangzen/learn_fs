# sources/user-network-fs/samba/source3/registry/reg_backend_tcpip_params.c

## Purpose
`reg_backend_tcpip_params.c` synthesizes TCP/IP parameter registry values, replacing an older dynamic overlay for host identity data.

## Important APIs, Types, And Functions
`tcpip_params_reg_ops` exports `.fetch_values` and `.fetch_subkeys`. `tcpip_params_fetch_values()` adds `Hostname` from `myhostname()` and `Domain` from `get_mydnsdomname(talloc_tos())`, both through `regval_ctr_addvalue_sz()` as `REG_SZ`. `tcpip_params_fetch_subkeys()` delegates to `regdb_ops.fetch_subkeys()`.

## Control Flow
The hook cache routes `KEY_TCPIP_PARAMS` to this backend. Fetching values produces the two dynamic values and returns the container count. Subkey enumeration is passed to the persistent registry database.

## State And Persistence
The dynamic values are not persisted; they reflect current host and DNS-domain information at fetch time. Temporary allocation for the DNS domain uses the top-of-stack talloc context.

## Dependencies And Integration Points
The file depends on Samba host-name helpers, `registry.h`, `reg_objects.h`, and `regdb_ops`. It is registered from `reg_init_full.c` under `KEY_TCPIP_PARAMS`.

## Risks And Test Signals
Tests should verify correct `REG_SZ` encoding, behavior when no DNS domain is configured, and consistency with `myhostname()` changes in the test environment. Subkey delegation should be covered separately. If the DNS helper can return `NULL`, callers should ensure `regval_ctr_addvalue_sz()` behavior remains acceptable.
