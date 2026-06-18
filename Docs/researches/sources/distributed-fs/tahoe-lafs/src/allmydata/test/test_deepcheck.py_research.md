# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_deepcheck.py

## Purpose
This module tests Tahoe-LAFS object check, repair, deep-check, deep-stats, manifest, CLI, and web API behavior across healthy, damaged, literal, mutable, immutable, directory, and large traversal scenarios. It exercises both programmatic node APIs and HTTP/CLI surfaces.

## Important APIs, types, and functions
- `run_cli` adapts `run_cli_unicode` to the existing varargs test style.
- `MutableChecker` tests mutable file web check and repair flows after corrupting or deleting shares.
- `DeepCheckBase` provides helpers for JSON web calls, streamed JSON parsing, operation-handle polling, and slow asynchronous web operations.
- `DeepCheckWebGood` constructs a mixed healthy tree and verifies `check`, `check_and_repair`, `start_deep_check`, `start_deep_check_and_repair`, `start_deep_stats`, stream manifest, web JSON, and CLI manifest/stats variants.
- `DeepCheckWebBad` builds a damaged tree and verifies healthy, missing-share, corrupt-share, and unrecoverable classifications with and without verification.
- `Large` checks that streaming deep-check over hundreds of literal files avoids Deferred tail-recursion overflow.

## Control flow
Healthy tests build a root directory containing mutable, CHK immutable, LIT files, empty/tiny LIT directories, and a loop back to root. The flow runs local stats, stream-manifest parsing, local node checks, web checks for all combinations of `verify` and `repair`, deep-check operations through operation handles, info pages, and CLI manifest/stats commands. The bad-tree flow builds mutable and large files for good, missing-share, corrupt-share, and unrecoverable cases, plus a broken subdirectory whose shares are mostly deleted. It compares non-verify checks, which do not detect corrupt shares, with verify checks, which do. Large traversal creates one CHK file plus 399 LIT children and validates streamed result count.

## State and persistence behavior
Test state is stored in in-memory attributes such as `root`, `mutable`, `large`, URI fields, and `nodes`, with persistent shares created in per-test basedirs by `GridTestMixin`. Damage is persisted by deleting shares, corrupting share data with `_corrupt_mutable_share_data`, and invoking `debug corrupt-share` through the CLI. Web operations persist status under `operations/<ophandle>` until the helper polls `finished`. Deep checks use `Monitor` objects, including explicit cancellation that must produce `OperationCancelledError`.

## Dependencies and integration points
The module depends on Twisted Deferreds and `inlineCallbacks`, Tahoe upload and mutable publishing APIs, mutable error types, check-result interfaces, `Monitor`, URI classes, grid/no-network test infrastructure, web HTTP helpers, CLI helpers, base32/idlib formatting, and JSON parsing. It is a broad integration test spanning node APIs, storage shares, web API query parameters, operation handles, streaming JSON protocols, and command-line output formats.

## Risks
Many assertions pin exact counters, output text, and CLI formatting, so changes to traversal semantics or presentation can require coordinated test updates. Corruption detection intentionally differs between verify and non-verify paths; regressions can hide if a code path starts reading too much or too little share data. The tree includes loops and LIT directories, so traversal must avoid infinite recursion and count only distributed objects where appropriate. Operation polling and large streamed outputs are asynchronous and can expose timing or buffering issues.

## Test signals
Signals include mutable repair success after corrupt/deleted shares, exact deep-stats counts and histograms, stream-manifest counts and cap classifications, JSON health fields and share maps, deep-check and deep-check-and-repair aggregate counters, cancellation failure with `OperationCancelledError`, CLI manifest raw/storage-index/verify-cap/repair-cap variants, damaged-tree classifications, unrecoverable deep-check failure on a broken subdirectory, and streamed line counts for hundreds of LIT files.
