# sources/storage-engines/foundationdb/fdbkubernetesmonitor/api/version.go

## Purpose
This Go file defines a FoundationDB `Version` type with parsing, JSON serialization, comparison, compatibility, and next-version helpers for the Kubernetes monitor.

## Important APIs, Types, And Functions
`Version` stores major, minor, patch, and release-candidate numbers. Functions/methods include `MarshalJSON`, `UnmarshalJSON`, `ParseFdbVersion`, `String`, `Compact`, `IsAtLeast`, `GetBinaryVersion`, `IsProtocolCompatible`, `NextMajorVersion`, `NextMinorVersion`, `NextPatchVersion`, and `Equal`.

## Control Flow
`ParseFdbVersion` applies regex `(\d+)\.(\d+)\.(\d+)(-rc(\d+))?`, converts captures to integers, and treats missing/invalid rc as zero. JSON unmarshal trims quotes and delegates to parse. Comparisons proceed major, minor, patch, then RC rules where stable releases outrank release candidates of the same major/minor/patch.

## State And Persistence Behavior
The type is pure in-memory value state. JSON methods persist versions as strings in configuration documents.

## Dependencies And Integration Points
It depends on `regexp`, `strconv`, `strings`, and `fmt`. It integrates with monitor configs and binary/library copy logic that needs compact major.minor or full rc-aware versions.

## Risks And Edge Cases
The regex is not anchored, so strings like `prerelease-6.2.11` parse successfully; this is covered by tests but may be surprising. Invalid rc conversion falls back to zero, though the regex only captures digits. Protocol compatibility treats different release candidates as incompatible.

## Test Signals
Existing tests cover parse variants, JSON round trips, formatting, compatibility, next-version helpers, equality, and RC-aware `IsAtLeast` ordering.
