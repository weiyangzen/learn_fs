# sources/sync-backup/borg/src/borg/testsuite/repoobj_test.py

## Purpose
Tests Borg repository object formatting/parsing for Borg 2 objects, legacy Borg 1 objects, Borg 1 to Borg 2 transfer behavior, malformed objects, and repository-object type spoofing. It validates authenticated metadata/data boundaries around `RepoObj`, `RepoObj1`, `PlaintextKey`, `LZ4`, and object type constants.

## Important APIs, Types, and Functions
Fixtures create a `Repository` and `PlaintextKey`. Tests exercise `RepoObj.format`, `parse`, `parse_meta`, `extract_crypted_data`, `id_hash`, and legacy `RepoObj1.parse`. Security/error paths expect `IntegrityError`.

## Control Flow
Round-trip tests format data, parse metadata first, parse full data, and inspect encrypted payload prefixes. Transition coverage reads Borg 1 compressed data with `want_compressed=True` and writes Borg 2 with explicit `size`, `ctype`, and `clevel`. Malformation tests build too-short or inconsistent headers and assert clean rejection.

## State and Persistence Behavior
The tests use temporary repositories but primarily exercise serialized in-repository object bytes. Metadata such as `size`, `csize`, `ctype`, and `clevel` is persisted inside the object envelope and must stay consistent with raw payload boundaries.

## Dependencies and Integration Points
Integrates repository object codecs, key encryption framing, compression metadata, constants for file streams/manifests/archive metadata, and transfer code assumptions that Borg 1 objects can be copied without decompression.

## Risks and Test Signals
Risks are silent data corruption, uncaught `struct.error`/`IndexError`, metadata/header length confusion, and object type spoofing. Strong signals are exact metadata values, data equality, prefix bytes, Borg 1 csize adjustment, and `IntegrityError` for malformed/spoofed objects.
