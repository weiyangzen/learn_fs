# sources/sync-backup/borg/src/borg/version.py

## Purpose
Implements Borg's simple version string parser and formatter for a protocol-stable integer tuple representation. It intentionally supports only `major.minor.patch` plus known prerelease forms.

## Important APIs, Types, and Functions
Exports `parse_version(version)` and `format_version(version)`. Prerelease mapping is `dev -> -9`, `a -> -4`, `b -> -3`, `rc -> -2`; final versions append `-1`.

## Control Flow
`parse_version` matches a verbose regex from the start of the string, extracts numeric parts, and appends prerelease markers if the optional group matched. `format_version` iterates tuple parts until it sees a negative sentinel, appending prerelease text to the previous numeric component.

## State and Persistence Behavior
No runtime persistence. The tuple format is part of the remote protocol, so changes persist externally as compatibility behavior between Borg versions.

## Dependencies and Integration Points
Depends only on `re`. Consumed by version tests and remote/protocol code that compares tuples lexicographically.

## Risks and Test Signals
Risks include regex accepting unwanted suffixes by prefix match, breaking tuple ordering, unknown negative markers causing `KeyError`, and malformed tuples. Tests cover valid/invalid parsing and canonical formatting.
