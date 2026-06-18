# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_hints.c

## Purpose
Implements kernel resource hint lookup, merging static hints into the dynamic environment and exposing typed query helpers for device configuration hints.

## Key Elements
- Static hint merge: `static_hints_to_env()`.
- Environment search backend: `res_find()`.
- High-level search: `resource_find()`.
- Typed accessors: `resource_int_value()`, `resource_long_value()`, `resource_string_value()`.
- Iterators: `resource_find_match()`, `resource_find_dev()`.
- Helpers: `resource_disabled()`, `resource_unset_value()`.

## Behavior
At `SI_SUB_KMEM + 1`, static hints are copied into the dynamic kernel environment unless an overriding value already exists. Before that merge, lookup falls back through machine-dependent environment, static environment, then `static_hints`; after the merge, dynamic environment is authoritative.

Hints must match the format `hint.<name>.<unit>.<resname>=<value>`. `resource_find()` first searches exact units, then wildcard unit `-1`. It can filter by device name, unit, resource name, and value, and can return non-null-terminated name/resource spans or value pointers. Invalid hint strings are reported and mutated from `hint.` to `Hint.` to avoid repeated parsing.

Typed accessors parse integer or long values with `strtoul`, return strings by pointer, and report `EFTYPE` on malformed values.

## Research Notes
The static buffer in `resource_string_copy()` makes iterator results convenient but not generally reentrant. Dynamic environment traversal is protected by `kenv_lock`.
