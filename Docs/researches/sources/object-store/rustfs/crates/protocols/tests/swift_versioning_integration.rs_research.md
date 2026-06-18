# sources/object-store/rustfs/crates/protocols/tests/swift_versioning_integration.rs

## Purpose

This Swift-feature-gated module comprehensively tests Swift object-version name generation. It focuses on the string contract used to archive object versions: an inverted timestamp prefix followed by container and object path segments. The tests cover format, ordering, path preservation, special characters, timestamp precision, uniqueness under sequential and concurrent generation, and cleanup/listing assumptions.

## Important APIs, types, and functions

- Imports `rustfs_protocols::swift::versioning::*`; the primary exercised API is `generate_version_name(container, object) -> String`.
- Version strings are expected to split as `{inverted_timestamp}/{container}/{object}` with `splitn(3, '/')` for ordinary containers.
- The timestamp component is expected to contain a decimal point, have a 10-digit whole part in stability tests, and have exactly nine fractional digits.
- Inverted timestamps are expected to make newer versions lexicographically smaller, so simple sorting can list newest versions first.
- Standard library concurrency primitives `Arc`, `Mutex`, and `thread` are used to stress concurrent generation.

## Control flow

The module creates version names under different timing and input scenarios. Format tests split the string and inspect timestamp and path components. Ordering tests generate versions with sleeps and compare adjacent strings. Precision and stress tests generate many names, count unique values with a `HashSet`, and enforce acceptable collision-rate thresholds rather than perfect uniqueness. Path tests assert version names preserve nested object paths and even container strings containing slashes. Metadata and cleanup tests verify surrounding structures that versioning workflows rely on.

## State and persistence behavior

There is no direct persistence. The version name itself encodes ordering state through current system time. The concurrent stress test stores generated strings in a mutex-protected vector. The metadata preservation test uses a local `HashMap` to model metadata that archive/restore workflows should preserve, but no archival storage is invoked.

## Dependencies and integration points

The tests depend on the Swift versioning helper and the system clock. In production, these version names integrate with object-copy or archive workflows where current objects are moved to a versions container/prefix and later restored on delete. The format is also an integration contract for listing, cleanup, and parsing because callers infer timestamp, container, and object from slash-delimited strings.

## Risks and edge cases

- Tests that depend on sleep duration and system clock precision can be flaky on very slow, very fast, or low-resolution platforms.
- Collision thresholds acknowledge that timestamp-only names are not a complete uniqueness mechanism under concurrent writes. The comments say production should use additional mechanisms such as UUIDs if strict uniqueness is required.
- Containers containing slashes make naive `splitn(3, '/')` parsing ambiguous. One test checks preservation for `"photos/2024"`, while another parser-style test assumes ordinary no-slash container names.
- Performance test includes 1000 sleeps of 10 microseconds but asserts total runtime below 200 ms, which may be tight under loaded CI.
- Empty container and object names are accepted by the generator tests even though they may not be valid Swift object names in production.

## Test signals

The suite strongly signals the expected version-name string contract: inverted timestamp, nine fractional digits, lexicographic newest-first sorting, and path preservation. It also documents tolerated collision rates and parser assumptions. It does not test actual PUT archive, DELETE restore, cross-account isolation in storage, or metadata persistence through real object operations.
