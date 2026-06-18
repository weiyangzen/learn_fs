# sources/object-store/daos/src/container/srv_layout.c

## Purpose
Defines the RDB string keys and default container property sets described by `srv_layout.h`. It also initializes and finalizes dynamically allocated default ACL entries used by container creation.

## Important APIs and data
- `RDB_STRING_KEY(ds_cont_prop_, ...)` and `RDB_STRING_KEY(ds_cont_attr_, user)` instantiate global `d_iov_t` keys for root/container property KVS entries.
- `cont_prop_entries_default_v0` is the older default property set with checksum and server verification enabled and RF3/rank redundancy defaults.
- `cont_prop_entries_default` is the current default property set with checksum/server verification off, RF0/default redundancy, and extra EC/PDA/global/scrubber/object/perf-domain fields.
- `cont_prop_default_v0` and `cont_prop_default` wrap those arrays as `daos_prop_t`.
- `ds_cont_prop_default_init()` allocates default DAOS container ACLs for both property sets.
- `ds_cont_prop_default_fini()` frees those ACL pointers.

## Control flow
Most of the file is static initialization. At module startup, `ds_cont_prop_default_init()` finds the ACL entries by type and fills `dpe_val_ptr` using `ds_sec_alloc_default_daos_cont_acl()`. If allocation of the current ACL fails after v0 allocation succeeded, it frees the v0 allocation before returning `-DER_NOMEM`. At shutdown, `ds_cont_prop_default_fini()` looks up both ACL entries and frees their value pointers.

## State and persistence behavior
The global `d_iov_t` key objects are used as stable RDB keys throughout the container service. The default property arrays are in-process templates copied/consulted by creation and migration logic; they are not persistent by themselves. `dummy_roots` avoids per-use allocation for the default roots property and is expected to be overwritten by middleware when real roots are set.

## Dependencies and integration
Depends on `daos_srv/rdb.h` for key macros and `daos_srv/security.h` for default ACL allocation. Service files use these globals for RDB lookup/update, and property conversion code depends on the default property coverage matching `DAOS_PROP_CO_*` ranges and version expectations.

## Risks
The default arrays must stay aligned with `CONT_PROP_NUM_V0`, `CONT_PROP_NUM`, and DAOS property enum ranges. Adding a property in `srv_layout.h` without adding defaults or conversion support can produce missing values in older code paths. The ACL pointers are mutable global state; double init/fini or partial initialization bugs can leak or double-free.

## Test signals
Tests should verify init/fini under allocation failure, default property counts, current versus v0 defaults, and that all optional container property types expected by creation/query have defaults. RDB layout compatibility tests should verify key names remain stable.
