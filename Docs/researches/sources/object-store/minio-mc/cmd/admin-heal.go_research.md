# sources/object-store/minio-mc/cmd/admin-heal.go

## Purpose
Implements `mc admin heal`, which reports background healing or starts, stops, and follows explicit heal operations over buckets, prefixes, pools, and sets.

## Important APIs, types, and functions
Key symbols include `adminHealFlags`, `adminHealCmd`, `checkAdminHealSyntax`, `stopHealMessage`, disk/server summary types, `generateSetsStatus`, `generateServersStatus`, `computePoolTolerance`, `verboseBackgroundHealStatusMessage`, `shortBackgroundHealStatusMessage`, `transformScanArg`, and `mainAdminHeal`.

## Control flow
The handler validates one target and scan mode, creates admin and object clients, parses bucket/prefix from the aliased URL, and branches. With no bucket and no recursive flag it fetches `BackgroundHealStatus` and prints short or verbose status. Otherwise it builds `madmin.HealOpts`, handles pool/set indexes, optionally stops a heal, prompts before full recursive namespace scans, starts healing, and hands the client token to `uiData.DisplayAndFollowHealStatus`.

## State and persistence behavior
Server-side healing tasks and background heal state are persistent operational state. Locally the command only tracks selected options, confirmation input, and the UI counters. `force-start`, `force-stop`, `remove`, `dry-run`, and `rewrite` directly affect server behavior.

## Dependencies and integration points
It integrates MinIO admin heal APIs, object URL parsing via `newClient`, terminal confirmation, hidden pool/set scan controls, global context, color themes, humanized summaries, and the heal UI/result helpers.

## Risks and edge cases
Full recursive healing is dangerous enough to require terminal confirmation unless `--force` is used. Pool and set flags are one-based externally and converted to zero-based pointers. Background tolerance calculations depend on parity and disk state accuracy. Some hidden flags have high operational impact.

## Test signals
Tests should cover syntax and scan validation, background status branches, verbose tolerance output, pool/set validation, force-stop payload, confirmation abort and proceed paths, heal option construction, token follow-up calls, and failure-detail tracing.
