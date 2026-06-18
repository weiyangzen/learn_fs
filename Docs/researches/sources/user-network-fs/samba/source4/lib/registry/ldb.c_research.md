# sources/user-network-fs/samba/source4/lib/registry/ldb.c

`ldb.c` implements a registry hive backend stored in LDB. Keys are LDB entries under `hive=NONE` with `key=` RDNs; non-default values are child entries with `value=` RDNs, while default values live as `data`/`type` attributes on the key entry. `struct ldb_key_data` caches the LDB context, DN, subkey/value search results, and classname. The backend implements open/add/delete key, enumerate key/value, set/get/delete value, and key info.

Value packing/unpacking maps registry types to LDB attributes: strings convert UTF-16 to/from UTF-8, DWORD/QWORD values are stored as numeric strings, and binary data is stored raw. `reg_open_ldb_file()` connects through `ldb_wrap_connect()`, adds `@ATTRIBUTES` case-insensitive rules, and returns a root hive key. Key deletion recursively deletes child keys and values inside an LDB transaction. Set value tries modify first and falls back to add.

Persistence is the LDB database file. Risks include cache invalidation correctness, no implemented security descriptor or flush hooks, type conversion failures producing empty data, transaction nesting during recursive delete, and root DN assumptions. Tests should cover all registry value types, default values, recursive delete, case-insensitive key/value names, and reopen persistence.
