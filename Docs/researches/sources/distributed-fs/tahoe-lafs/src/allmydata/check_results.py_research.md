# sources/distributed-fs/tahoe-lafs/src/allmydata/check_results.py

## Purpose

This module provides result containers for file checks, check-and-repair operations, deep-check traversals, and deep-check-and-repair traversals. It adapts checker output into stable interfaces and serializable counters used by CLI/web/API consumers.

## Important APIs, Types, And Functions

`CheckResults` implements `ICheckResults` and stores URI, storage index, health/recoverability, share counters, server lists, share maps, corrupt/incompatible share lists, reports, share problems, and optional mutable servermap. `CheckAndRepairResults` implements `ICheckAndRepairResults` with pre/post results and repair flags. `DeepResultsBase` stores root storage index, aggregate result maps, corrupt shares, and stats. `DeepCheckResults.add_check()` and `get_counters()` aggregate plain checks. `DeepCheckAndRepairResults.add_check_and_repair()`, `get_counters()`, and `get_remaining_corrupt_shares()` aggregate repair-aware results.

## Control Flow

Checkers instantiate `CheckResults` with detailed counters and lists. The constructor validates URI/server interfaces and normalizes byte summaries to text. Deep traversal code calls `add_check()` or `add_check_and_repair()` for each distributed object; LIT/non-distributed falsey results are ignored. Each add method updates counters, stores path-indexed and storage-index-indexed results, and extends corrupt share lists. API consumers call getters or `as_dict()`/`get_counters()`.

## State And Persistence

All state is in-memory result data. There is no direct persistence, but these objects are serialized or rendered by higher-level web/CLI code. `all_results` is keyed by path tuple, and `all_results_by_storage_index` is keyed by raw storage index.

## Dependencies And Integration Points

It depends on interfaces from `allmydata.interfaces`, base32 encoding, and mutable `ServerMap` validation when servermap data is present. It integrates with file node `check`, repair, directory deep traversal, web status, and CLI reporting.

## Risks

The constructors rely heavily on assertions, which can be disabled with optimized Python and are not user-facing validation. `CheckAndRepairResults` initializes only `repair_attempted`; callers must set `repair_successful`, `pre_repair_results`, and `post_repair_results` before getters are used. Duplicate storage indexes overwrite previous entries in `all_results_by_storage_index`. Some result fields may contain bytes while API consumers expect JSON-friendly data.

## Test Signals

Construct healthy/unhealthy/recoverable/unrecoverable results, verify summary defaults and `as_dict()` server ID conversion, test corrupt/incompatible share propagation, ensure LIT falsey results are ignored in deep counters, and verify repair counters for attempted/successful/failed repairs.
