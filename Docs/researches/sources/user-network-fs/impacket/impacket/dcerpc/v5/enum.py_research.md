# sources/user-network-fs/impacket/impacket/dcerpc/v5/enum.py

## Purpose

`enum.py` provides a local Python enumeration implementation compatible with older Python versions and Impacket's NDR enum classes. It mirrors enough standard-library `Enum`, `IntEnum`, and `unique` behavior for protocol modules to define symbolic numeric values portably.

## Important APIs, Types, And Functions

The public API is `Enum`, `IntEnum`, and `unique`. Internal helpers include `_RouteClassAttributeToGetattr`, `_is_descriptor`, `_is_dunder`, `_is_sunder`, `_make_class_unpicklable`, and `_EnumDict`. `EnumMeta` implements enum class creation, lookup, iteration, containment, member protection, functional API support, mixin resolution, and Python-version-specific member construction.

The runtime `Enum` class is built from `temp_enum_dict` and supports value lookup, representation, string conversion, formatting, comparison behavior, pickling arguments, hashing, and protected `name`/`value` properties. `IntEnum` mixes `int` with `Enum`; `unique` rejects aliases.

## Control Flow

`EnumMeta.__prepare__` returns `_EnumDict` to track member order. `EnumMeta.__new__` resolves mixins, extracts member definitions, creates the enum class, instantiates members, handles duplicate-value aliases, and builds `_member_names_`, `_member_map_`, and `_value2member_map_`. `EnumMeta.__call__` performs by-value lookup or functional class creation. `Enum.__new__` checks hash lookup first, falls back to linear search for unhashable values, and raises `ValueError` on misses.

## State And Persistence Behavior

Enum state is in class metadata: `_member_names_`, `_member_map_`, `_member_type_`, and `_value2member_map_`. There is no external persistence. Pickling is disabled for some mixed-in enum classes when stable reconstruction is not possible.

## Dependencies And Integration Points

The module depends only on `sys`. Protocol modules such as `drsuapi.py` and `dssp.py` use it for nested `enumItems(Enum)` classes so NDR enum dumps can resolve known numeric values to names.

## Risks And Edge Cases

Subtle divergence from Python's standard `enum` can affect all protocol modules. `_create_` assumes non-empty `names` in some paths and references the loop variable after iteration. Duplicate values become aliases unless `unique` is used. Unhashable values require linear lookup. Old Python compatibility branches are hard to exercise on modern runtimes.

## Test Signals

Tests should cover class syntax, functional API creation, aliases, `unique`, `IntEnum`, by-name/by-value lookup, iteration order, reassignment/deletion errors, `name` and `value` property routing, and representative NDR enum dump behavior.
