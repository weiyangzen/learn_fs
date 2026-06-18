# sources/user-network-fs/samba/source3/registry/reg_backend_prod_options.c

## Purpose
`reg_backend_prod_options.c` provides a dynamic Product Options registry backend. Its main job is to synthesize the Windows `ProductType` value from Samba's configured server role.

## Important APIs, Types, And Functions
`prod_options_reg_ops` exports `.fetch_values` and `.fetch_subkeys`. `prod_options_fetch_values()` calls `lp_server_role()` and maps domain controller roles to `LanmanNT`, standalone servers to `ServerNT`, and domain members to `WinNT`. The value is added with `regval_ctr_addvalue_sz()` as `REG_SZ`. `prod_options_fetch_subkeys()` delegates enumeration to `regdb_ops`.

## Control Flow
When the registry dispatcher fetches values for the hooked Product Options key, this backend computes the role string, inserts `ProductType`, and returns the current value count. It does not inspect the requested key beyond receiving it from the hook machinery, relying on `reg_init_full.c` to bind it to `KEY_PROD_OPTIONS`.

## State And Persistence
The backend is read-only for dynamic values and persists nothing. Subkeys can still come from the default registry database because subkey fetches pass through to `regdb_ops`.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_objects.h`, `lp_server_role()`, Samba role constants, and the default registry database operations. It is registered by `registry_init_full()` under `KEY_PROD_OPTIONS`.

## Risks And Test Signals
Role-to-string compatibility is the main behavior to protect. Tests should simulate or configure each server role and verify the exact `ProductType` string and `REG_SZ` encoding. A future enum value could silently leave `value_ascii` empty, so tests around all known roles are useful. Subkey delegation should also be checked if stored child keys are expected below this virtual path.
