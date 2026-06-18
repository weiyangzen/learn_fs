# sources/sync-backup/casync/src/caformat-util.h

## Purpose
Declares the format utility API for translating casync feature flags, record types, filesystem attributes, and digest choices.

## Important APIs, Types, and Functions
Exports type naming, feature parse/format, normalization, mask normalization, time granularity lookup, chattr/FAT attr conversions, filesystem magic feature detection, normalized-mask validation, and digest feature conversion.

## Control Flow
The header has no implementation flow; it is a shared utility contract used before writing or after reading format headers.

## State and Persistence Behavior
No state is declared. Return values determine canonical feature masks persisted in archive and index records.

## Dependencies and Integration Points
Includes `cadigest.h` and `util.h`, particularly for `CaDigestType` and `statfs_f_type_t`. Integrated by encoder, index, FUSE, and command-line feature handling.

## Risks
Because normalization errors propagate into persisted metadata, callers should check all negative returns. `ca_feature_flags_to_digest_type` treats absence of the SHA512/256 bit as SHA-256.

## Test Signals
Header compile coverage and API-level unit tests for each conversion function are sufficient.
