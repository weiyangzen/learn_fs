# sources/user-network-fs/samba/source4/lib/registry/local.c

`local.c` implements a registry context that mounts hive roots under predefined HKEY paths. `reg_open_local()` creates a `registry_local` context with `local_ops`; `reg_mount_hive()` attaches a `hive_key` at a predefined key and optional path; `reg_import_hive_key()` wraps a hive key as a registry key. Operations split registry paths, walk or create hive keys, and forward value, enumeration, info, security, delete, and flush operations to the mounted hive.

State persists through mounted hive backends, while `registry_local` holds only mountpoint metadata and talloc references. `local_open_key()` and `local_create_key()` maintain path element arrays so wrapped keys know their absolute position. Integration is the bridge from high-level `registry_context` APIs in `interface.c` to low-level `hive_operations` in `hive.c`/`ldb.c`/REGF.

Risks include mountpoint lookup only returning exact predefined roots with NULL elements in `local_get_predefined_key()`, path element allocation size needing NULL terminators, no duplicate mountpoint protection, and forwarding backend limitations. Tests should mount hives under multiple HKEY roots, create nested keys, delete values, flush, and check security descriptor propagation.
