# sources/object-store/openstack-swift/swift/common/utils/timestamp.py

## Purpose
This module implements Swift's canonical timestamp model. It provides fixed-width, lexicographically sortable normal timestamps and extended internal timestamps with a hex offset used to order otherwise identical object events. It also encodes multiple logical object timestamps into compact database/file-name strings.

## Important APIs, Types, and Functions
- `BaseTimestamp` supplies parsing/creation plumbing, deca-microsecond rounding (`PRECISION = 1e-5`), bounds checks, normal/internal string properties, ordering, hashing, `isoformat`, `from_isoformat`, `ceil`, and inversion.
- `NormalTimestamp` rejects underscores and represents only the normalized float component.
- `Timestamp` adds a non-negative 16-hex-digit offset, `internal`, `short`, `increment_offset()`, `normalized()`, offset-aware truthiness, and offset-aware inversion.
- `encode_timestamps(t1, t2=None, t3=None, explicit=False)` serializes up to three timestamps as a base timestamp plus signed hex deltas.
- `decode_timestamps(encoded, explicit=False)` reverses that encoding and returns `(t1, t2, t3)`, defaulting missing values to previous values unless `explicit=True`.
- `normalize_timestamp()`, `last_modified_date_to_timestamp()`, and `normalize_delete_at_timestamp()` convert external formats into Swift's sortable string conventions.

## Control Flow and Behavior
Construction coerces numeric inputs through `_create()` and non-numeric inputs through `_parse()`, then rounds to a raw deca-microsecond integer and optionally applies `delta`. Comparison uses the `internal` string after coercion, preserving stable sort semantics across normal and extended forms. `Timestamp._parse()` splits at one underscore and validates both count and hex width; `offset` assignment ignores falsy zero, preserving the initialized zero offset.

`encode_timestamps()` stores `t1.short` and appends `+/-` hex deltas for `t2 - t1` and `t3 - t2` only when needed or explicit. This is used by object metadata rows where data, content-type, and metadata timestamps may differ. `decode_timestamps()` reconstructs distinct `Timestamp` objects only for non-zero deltas, preserving any offset in `t1` for equal components.

## State and Persistence
There is no external persistence here, but timestamp strings produced by this module are persisted throughout Swift object, container, and reconciler state. Constants define the on-disk/on-wire contract: `NORMAL_FORMAT`, `INTERNAL_FORMAT`, `SHORT_FORMAT`, `HEX_PART_DIGITS`, `MAX_OFFSET`, and `MAX_RAW_TIME`. `FORCE_INTERNAL` is module-level state used mainly by tests or upgrade scenarios to force extended formatting.

## Dependencies and Integration Points
This module is imported by container backend, reconciler, object metadata handling, database naming, expirer logic, HTTP Last-Modified conversion, and most consistency code. It relies only on Python `datetime`, `functools`, `math`, and `time`, making it a foundational low-level utility.

## Risks and Edge Cases
- Ordering correctness depends on fixed-width normal/internal string formats; changing width or precision would corrupt persisted sort semantics.
- `normalize_delete_at_timestamp()` caps values at `9999999999.99999` to preserve expirer container-name sorting; this is a deliberate long-term limitation.
- `BaseTimestamp.__lt__()` treats out-of-range coerced values specially when bounds checks were bypassed, so tests should cover invalid comparisons.
- Offsets cannot exceed `MAX_OFFSET`, and `delta` cannot move raw time below zero.
- `EPOCH` is timezone-naive while `isoformat` uses UTC-aware conversion then strips the timezone suffix; this is intentional but easy to misuse.

## Test Signals
High-value tests include lexicographic ordering across normal and internal forms, offset increment and max validation, inversion ordering, explicit and implicit multi-timestamp encoding, negative delta rejection, bytes parsing, isoformat round-trips, delete-at clamping, and compatibility with strings lacking extended offsets.
