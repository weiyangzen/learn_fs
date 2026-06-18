# sources/storage-engines/tikv/components/engine_traits/src/cf_defs.rs

Purpose: Defines canonical TiKV column-family names and helper mappings for data CF indexing.

Important APIs and control flow: Constants include `CF_DEFAULT`, `CF_LOCK`, `CF_WRITE`, `CF_RAFT`, `LARGE_CFS`, `ALL_CFS`, `DATA_CFS`, and `DATA_CFS_LEN`. `data_cf_offset` treats empty CF as default and returns the index in `DATA_CFS`; `offset_to_cf`, `name_to_cf`, and `is_data_cf` provide reverse and validation helpers.

State, persistence, and dependencies: No runtime state is stored. These constants align engine metadata, flush-state arrays, range accounting, and tests.

Integration points, risks, and test signals: Used widely by KvEngine, flush/apply persistence, range estimates, and test constructors. Risks include panics from unknown CFs in `data_cf_offset`, array-index assumptions if CF sets change, and treating empty string as default in only some APIs. Tests in `cf_names` and many CF-specific scenarios exercise these constants.
