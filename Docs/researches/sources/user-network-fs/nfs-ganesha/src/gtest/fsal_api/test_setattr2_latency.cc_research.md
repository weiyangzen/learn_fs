# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_setattr2_latency.cc

## Purpose
This executable measures `setattr2` and `fsal_setattr` latency on cached and many-object access patterns. It updates attributes on one test file and on many looked-up files in a primed directory.

## Important APIs, Types, And Functions
`Setattr2EmptyLatencyTest` creates `setattr2_test_file` with `fsal_create` and removes it with `fsal_remove`. `Setattr2FullLatencyTest` primes 100,000 entries. Tests call `obj_ops->setattr2`, `fsal_setattr`, `obj_ops->lookup`, and `mdcdb_get_sub_handle`. Attributes come from the base fixture's `attrs`, initialized with mode, owner, and group.

## Control Flow, State, And Persistence
Simple tests set attributes once through normal and bypass handles. `FSAL_SETATTR` loops over the wrapper on the same file. `BIG_CACHED` repeatedly mutates the same file in a large directory. `BIG_UNCACHED` first looks up all primed file handles and cycles through them for one million attribute updates. Bypass uncached tests map each looked-up object to a sub-handle before timing.

## Dependencies And Integration Points
The test integrates with FSAL attribute lists, lookup/reference ownership, MDCACHE bypass, and the base helper's `create_and_prime_many` naming scheme. It exercises both wrapper and direct object operation layers.

## Risks And Test Signals
The uncached variants keep 100,000 object references and sub-handle pointers, which can stress memory and reference accounting. The test repeatedly applies the same attributes, so backends may optimize away changes after the first call. There is no postcondition verifying attribute values; status assertions and cleanup are the main signals.
