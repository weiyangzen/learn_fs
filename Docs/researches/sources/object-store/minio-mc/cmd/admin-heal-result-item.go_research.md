# sources/object-store/minio-mc/cmd/admin-heal-result-item.go

## Purpose
Wraps `madmin.HealResultItem` with helper methods that compute health-color transitions and display names for heal output.

## Important APIs, types, and functions
`hri` embeds `*madmin.HealResultItem`. Helpers include `newHRI`, `getObjectHCCChange`, `getBucketHCCChange`, `getReplicatedFileHCCChange`, `makeHealEntityString`, `getHRTypeAndName`, and `getHealResultStr`.

## Control flow
Each color helper inspects before/after drive or shard counts and maps them to `col` values. Object healing uses data and parity blocks plus online counts. Bucket healing classifies drive states as ok, missing, or unavailable. Replicated metadata computes quorum and surplus either per set or per disk count.

## State and persistence behavior
This file is pure presentation logic over server-returned heal records. It does not store state; it derives before/after color state from the `HealResultItem` snapshot.

## Dependencies and integration points
It depends on `madmin-go` heal item types and drive states, the `col` type and `getHColCode` from heal UI code, and formatting conventions used by quiet, JSON, and interactive heal displays.

## Risks and edge cases
Nil heal items return a grey/grey bucket result with an error. Invalid parity or surplus values bubble as errors, so display code must handle malformed server records. Metadata quorum math differs when `SetCount` is positive versus bucket-level healing.

## Test signals
Tests should exercise all heal item types, nil bucket input, missing/unavailable drives, object parity ranges, replicated metadata with and without set count, and unknown item types in name formatting.
