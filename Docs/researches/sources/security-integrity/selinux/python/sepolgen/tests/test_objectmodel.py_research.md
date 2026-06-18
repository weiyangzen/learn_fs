# sources/security-integrity/selinux/python/sepolgen/tests/test_objectmodel.py

## Purpose
This file tests permission mapping loading and default behavior in `sepolgen.objectmodel.PermMappings`.

## Important Tests And Exercised APIs
`TestInfoFlow.test_from_file()` constructs `PermMappings`, opens local `perm_map`, loads it with `from_file()`, then checks `get("filesystem", "mount")` returns a mapping with permission `mount`, write-flow direction, and weight `1`. It verifies missing known-class permissions raise `KeyError`, while `getdefault()` returns default mappings with both-direction flow and weight `5`.

## Control Flow
The test reads the permission map fixture, performs one concrete lookup, one failing lookup, and two default lookups.

## State And Persistence
State is the in-memory permission map loaded from `perm_map`. The file is read only.

## Dependencies And Integration Points
It depends on `sepolgen.objectmodel` and the local `perm_map` data file. This data corresponds to the shared file installed by `src/share/Makefile`.

## Risks And Edge Cases
The test assumes the current working directory contains `perm_map`. It validates only one real mapping from the fixture, so broad format regressions may escape unless they affect loading or the checked entry.

## Test Signals
It gives a targeted signal for permission-map parsing, lookup failure, and fallback defaults used by information-flow or matching logic.
