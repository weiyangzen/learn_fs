# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/access.py

## Purpose
This module defines core in-memory representations for SELinux access: single access vectors, deduplicated access-vector sets, and role-type statements. It is a foundational sepolgen data model used by audit parsing, interface matching, and policy generation.

## Important APIs, types, and functions
- `is_idparam(id)` identifies interface parameters of the form `$N`.
- `AccessVector` stores `src_type`, `tgt_type`, `obj_class`, permissions, audit messages, audit2why rule type, auxiliary data, extended permissions, and information-flow direction. Key methods are `from_list()`, `to_list()`, `merge()`, `to_string()`, and `_compare()`.
- `avrule_to_access_vectors(avrule)` expands a refpolicy AVRule with multiple source types, target types, or object classes into individual `AccessVector` objects.
- `AccessVectorSet` stores non-overlapping vectors in nested dictionaries by source, target, and `(object class, audit2why type)`. It exposes iteration, length, `to_list()`, `from_list()`, `add()`, and `add_av()`.
- `avs_extract_types()` collects source and target types from vectors.
- `avs_extract_obj_perms()` maps object classes to all permissions observed for that class.
- `RoleTypeSet` deduplicates `role types` statements by role and accumulates types.

## Control flow
`AccessVector.from_list()` treats the first three list elements as source, target, and class, and all remaining elements as permissions. `AccessVectorSet.add()` builds an `AccessVector` from explicit arguments and delegates to `add_av()`. `add_av()` creates the nested dictionary buckets and either merges permissions/xperms into an existing vector with the same key or stores the new vector. Audit messages are appended to the merged vector when supplied.

## State and persistence behavior
All state is in-memory. `to_list()`/`from_list()` provide a simple serialization shape for other modules to write/read, but this module performs no file I/O. Merging mutates permission and extended-permission sets in existing vectors.

## Dependencies and integration points
It imports local `refpolicy` and `util`, and `selinux.audit2why`. The module expects `refpolicy.IdSet`, `refpolicy.XpermSet`, and `refpolicy.RoleType`. `audit.py` creates `AccessVector` instances from AVC records. `interfaces.py` uses `is_idparam()`, `avrule_to_access_vectors()`, and `AccessVectorSet` for interface analysis and expansion.

## Risks and edge cases
- `AccessVector.__init__` sets `self.__hash__ = None` on the instance, which does not actually make the class unhashable in the same way as defining `__hash__ = None` at class scope.
- `AccessVectorSet.add()` uses `data=[]` as a default argument. It assigns the list to each created vector, so callers that mutate shared default data could leak state.
- `AccessVectorSet.__len__()` is O(N) over nested maps.
- `AccessVector.merge()` merges permissions and xperms but does not merge metadata such as `data`, `type`, or `info_flow_dir`; this is intentional for same-key vectors but can hide differences if callers expect full provenance.
- `avrule_to_access_vectors()` copies `perms` but not other AVRule metadata.

## Test signals
Focused tests should cover list round-tripping, permission merging, xperm merging, separate buckets for different audit2why types, `is_idparam()` validation, AVRule expansion, and extraction helpers. No tests are present in this subset.
