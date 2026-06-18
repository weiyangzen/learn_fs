# sources/object-store/daos/src/vos/storage_estimator/common/vos_structures.py

## Purpose
Object-builder classes for constructing valid storage-estimator YAML payloads in Python. They enforce a typed hierarchy of containers, objects, dkeys, akeys, and values.

## Important APIs, types, and functions
- Enums: `KeyType`, `Overhead`, `ValType`, and `StrBool`.
- `VosBase` stores `_payload`, validates integer `count`, and converts enum values.
- `VosValue` requires integer `size` and optional `aligned`.
- `VosItems` handles lists of child values and raises `VosValueError` when empty.
- `VosKey`, `AKey`, `DKey`, `VosObject`, and `Container` model estimator YAML nodes.

## Control flow
Constructors populate `_payload` dictionaries immediately. Higher-level nodes call `_add_values` to validate and dump child objects. `dump()` returns the underlying nested dictionaries only after non-empty child lists are verified.

## State and persistence behavior
State is transient Python dictionaries that can be serialized as YAML by callers. Hashed keys derive `size` from UTF-8 byte length when a key string is supplied; integer keys omit size. Defaults mark key overhead as user, values as aligned, and object/container counts as one.

## Dependencies and integration points
Used by DFS and CSV conversion code to generate YAML accepted by `MetaOverhead`. It integrates with `util.ProcessBase._get_yaml_from_dfs`, which creates `Containers`, adds DFS superblock/container data, sets checksum fields, and dumps the resulting payload.

## Risks and edge cases
Several constructors use mutable default arguments (`values=[]`, `akeys=[]`, `dkeys=[]`, `objects=[]`), which is normally risky even though the code only iterates over them. `_set_aligned` uses identity checks against strings, which can be unreliable. `_check_value_type` formats `type(self._values_type)` instead of the class itself, producing less useful error text.

## Test signals
Signals include exceptions on missing sizes/value types, rejected wrong child types, non-empty child enforcement, correct UTF-8 key-size calculation, and generated dictionaries matching fixture YAML schema.
