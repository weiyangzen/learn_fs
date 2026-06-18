# sources/user-network-fs/samba/source3/utils/regedit_wrap.c

`regedit_wrap.c` is a compatibility layer around Samba3 registry APIs, avoiding conflicts with Samba4 libregistry type names used by regedit. It presents wrapper functions that operate on `struct samba3_registry_key` and return `WERROR` values.

Important functions include hive/key open, value enumeration/query, subkey enumeration, key create/delete, value delete/set, key info query, and registry initialization. Value wrappers convert Samba3 `struct registry_value` results into the generic type plus `DATA_BLOB` representation expected by `regedit_samba3.c`.

Control flow is thin delegation. Hive opening creates an admin token and calls `reg_openhive` with read/write access. Key open/create also request read/write access. `reg_setvalue_wrap` builds a temporary `registry_value` and delegates to `reg_setvalue`.

The file owns no durable state; persistence happens in the underlying Samba3 registry storage. Dependencies are Samba3 registry headers, admin token utilities, and `regedit.h`. Risks include read-only UI operations failing because opens request write access, assertions on non-null output key reuse, and data lifetime depending on talloc contexts. Test signals: hive open, key create/delete, value set/query/delete, enumeration, info queries, and initialization failure propagation.
