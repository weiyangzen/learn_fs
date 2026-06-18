# sources/storage-engines/tikv/src/storage/txn/actions/mod.rs

## Purpose
Defines the storage transaction action module surface. These action modules are higher-level operations over `MvccTxn`, `MvccReader`, and `SnapshotReader` that command handlers compose into transactional behavior.

## Important APIs, types, and functions
This file exports modules: `acquire_pessimistic_lock`, `check_data_constraint`, `check_txn_status`, `cleanup`, `commit`, `common`, `flashback_to_version`, `gc`, `mvcc`, `prewrite`, and `tests`.

## Control flow
There is no runtime control flow. The documentation comment frames actions as groups of basic MVCC operations such as `MvccReader::load_lock` and `MvccTxn::put_write`.

## State and persistence behavior
No direct state mutation occurs here. State behavior is delegated to the exported action modules.

## Dependencies and integration points
This module is the namespace used by command handlers and tests, such as `txn::actions::commit::commit`, `txn::actions::prewrite::prewrite`, and shared testing helpers under `txn::actions::tests`.

## Risks and edge cases
Adding or removing exports here changes module visibility and can break command-layer imports. Exporting `tests` in normal module structure means test helpers are available under cfg-controlled uses elsewhere.

## Test signals
No direct tests. Build coverage and downstream module tests validate this module map.
