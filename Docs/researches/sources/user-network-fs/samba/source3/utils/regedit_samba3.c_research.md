# sources/user-network-fs/samba/source3/utils/regedit_samba3.c

`regedit_samba3.c` adapts Samba3 registry APIs into the generic `struct registry_operations` interface used by regedit. Private `struct samba3_key` embeds a generic `registry_key` plus a wrapped Samba3 key, and `struct samba3_registry_context` embeds a generic context.

The static `reg_backend_s3` table implements key open, predefined hive lookup, subkey/value enumeration, value get/set/delete, key create/delete, and key info. `reg_open_samba3` initializes the basic registry subsystem through `reg_init_wrap`, allocates the context, and installs this operation table.

Control flow is mostly delegation. Predefined hive lookup maps Windows hive constants to short names like `HKLM`, allocates a wrapped key, and calls `reg_openhive_wrap`. Other operations downcast generic keys using `talloc_get_type` and call wrapper functions from `regedit_wrap.c`.

Persistent state changes happen in the Samba3 registry through set/create/delete wrapper calls; this file stores no mutable global state beyond the backend table and hive map. Risks include ignored `key_class` and security descriptor arguments for create-key, unsupported hives returning `WERR_NO_MORE_ITEMS`, and read-oriented operations still requiring read/write opens. Test signals include opening hives, enumerating, querying, setting/deleting values, create/delete key round trips, and unsupported hive behavior.
