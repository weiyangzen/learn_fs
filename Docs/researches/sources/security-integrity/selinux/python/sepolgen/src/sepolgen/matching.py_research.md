# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/matching.py

## Purpose
This module scores requested SELinux access vectors against access vectors provided by reference-policy interfaces. It chooses interface matches that cover a requested access while preferring closer permission/type/object-class and information-flow behavior.

## Important APIs, Types, And Functions
`Match` stores an interface candidate, numeric distance, and whether the candidate changes information-flow direction. It inherits rich comparison behavior from `util.Comparison`, ordering by `(dist, info_dir_change)`. `MatchList` separates acceptable `children` from over-threshold or direction-changing `bastards`, exposes `best()`, `all()`, `append()`, and `sort()`, and records the requested `av`.

`AccessMatcher` owns distance penalties and a `objectmodel.PermMappings` instance. `type_distance()` treats exact matches and access id parameters as zero distance. `perm_distance()` computes missing permissions as negative distance and surplus provided permissions as positive distance using permission weights. `av_distance()` combines source type, target type, object class, and permission distance. `av_set_match()` scores an interface access set against one requested vector and penalizes write-capable interfaces for read-only requests. `search_ifs()` scans enabled interfaces by target type and populates a `MatchList`.

## Control Flow
The normal path is `PolicyGenerator` -> `InterfaceGenerator.match()` -> `AccessMatcher.search_ifs()`. `search_ifs()` considers generic target-type interfaces and target-specific interfaces, skips disabled interfaces, computes aggregate distance, accepts non-negative scores, and sorts results. `av_set_match()` caches `av_set.info_dir` after computing permission-flow direction across its rules.

## State And Persistence Behavior
All state is in-memory. `MatchList` accumulates matches for one requested access. `AccessMatcher` is reusable and keeps only configuration. Interface access sets may be mutated by caching `info_dir`, which is a cross-call performance optimization and an observable state side effect.

## Dependencies And Integration Points
It depends on `access` for id-parameter detection, `objectmodel` for permission weights and flow constants, and `util.Comparison` for ordering. It integrates with `interfaces.InterfaceSet`-like objects that expose `tgt_type_all`, `tgt_type_map`, and interface descriptors with `.enabled`, `.name`, and `.access`.

## Risks And Edge Cases
The distance model is heuristic and comments call out expense. Negative/positive distance combination is subtle and can reorder candidates unexpectedly when type/object mismatch and permission surplus combine. `Match.info_dir_change` is initialized but never set in the shown scorer even though `MatchList` checks it, so direction-changing candidates are penalized numerically but not flagged structurally. Mutating `av_set.info_dir` assumes the access set is stable. Threshold defaults may drop viable but broad interfaces.

## Test Signals
Tests should cover exact matches, id-parameter matches, missing and surplus permissions, object-class mismatches, multi-rule interface access sets, write-flow penalty for read-only requests, disabled interfaces, target-type maps, threshold behavior, and sorted best-match selection.
