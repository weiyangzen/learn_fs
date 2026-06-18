# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_common_util.py

## Purpose
This file tests shared test utilities: bit-flipping for corrupting byte strings and the `disable_modules` context manager used to simulate unavailable imports.

## Important APIs, Types, And Functions
Test classes are `TestFlipOneBit` and `DisableModulesTests`. It uses `flip_one_bit` from `allmydata.test.common_util`, `disable_modules` from `.common`, `namedAny`, `ModuleNotFound`, and Hypothesis strategies over existing top-level `sys.modules` entries.

## Control Flow
`TestFlipOneBit` seeds the random module for deterministic byte mutation and asserts bytes are accepted while Unicode strings are rejected. `DisableModulesTests` snapshots `sys.modules` around each Hypothesis example, verifies selected modules import before the context, verifies `namedAny` raises `ModuleNotFound` inside the context, then confirms imports work afterward. It also rejects dotted module names.

## State, Persistence, And Dependencies
The tests temporarily mutate `sys.modules` via `disable_modules` and restore from snapshots. There is no disk persistence. The strategy only selects currently importable top-level modules.

## Risks And Test Signals
The file catches leaks from simulated import blocking and type errors in corruption helpers. Because it uses live `sys.modules`, generated examples vary with the active test environment.
