# sources/storage-engines/tikv/src/server/ttl/mod.rs

## Purpose

This is the TTL server module facade. It declares the TTL checker and TTL compaction filter submodules and re-exports the public types used by the wider server and storage configuration code.

## Important APIs, Types, And Functions

Exports are `TtlCheckerTask`, `TtlChecker`, `check_ttl_and_compact_files`, and `TtlCompactionFilterFactory`. There is no local logic beyond module wiring.

## Control Flow

Consumers import through `server::ttl` instead of depending on the submodule paths. The config manager uses `TtlCheckerTask`; RocksDB setup can use `TtlCompactionFilterFactory`.

## State And Persistence Behavior

No state is stored in this module.

## Dependencies And Integration Points

This facade integrates `ttl_checker.rs` and `ttl_compaction_filter.rs` with server-level module naming.

## Risks And Edge Cases

The only risk is API surface drift: changes to submodule exports must be reflected here or downstream imports will break.

## Test Signals

No local tests are present; behavior is covered through the re-exported modules.
