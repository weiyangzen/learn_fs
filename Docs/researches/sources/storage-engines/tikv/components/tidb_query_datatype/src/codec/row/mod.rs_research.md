# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/row/mod.rs

## Purpose
This is the row codec module entry point. It currently exposes only the v2 row codec submodule.

## Important APIs, Types, and Functions
The file contains `pub mod v2;`, making `crate::codec::row::v2` available to downstream code. There are no local functions or types.

## Control Flow and State
There is no runtime control flow and no state. The file is purely a module declaration.

## Dependencies and Integration Points
It integrates the v2 row codec with the surrounding `codec` namespace. Consumers reach row-slice decoding, v1 compatibility, and test row encoders through this module tree.

## Risks and Edge Cases
The main risk is accidental module visibility changes. Removing or renaming this declaration would break all `codec::row::v2` imports. There are no direct tests for this file beyond compilation of downstream modules.

## Test Signals
Coverage is compile-time: all tests in `row/v2` depend on this module path being available.
