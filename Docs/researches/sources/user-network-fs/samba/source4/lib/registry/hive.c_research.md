# sources/user-network-fs/samba/source4/lib/registry/hive.c

`hive.c` is the generic registry hive wrapper layer. `reg_open_hive()` peeks at a file header and dispatches to `reg_open_regf_file()` for `regf` hives or `reg_open_ldb_file()` for LDB/TDB-backed hives. The remaining functions forward key operations to `struct hive_operations`: key info, add/delete/open/enumerate subkeys, set/get/enumerate/delete values, get/set security descriptors, and flush.

Control flow is intentionally thin and backend-driven. Optional operations return `WERR_NOT_SUPPORTED`, while `hive_key_flush()` treats a missing flush hook as success. State and persistence are entirely backend-owned; this file only chooses a backend and normalizes API behavior.

Risks include simplistic file-type detection using a short read, returning `WERR_FILE_NOT_FOUND` for several different open/read/unknown-format failures, and trusting backend operation tables. `hive_key_add_name()` asserts that names do not contain backslashes, so path splitting must happen above this layer. Test signals include opening REGF and LDB hives, unsupported optional operations, and operation forwarding against mock or local backends.
