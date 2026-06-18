# File Research: sources/virtualization/virtiofsd/src/soft_idmap/cmdline.rs

## Purpose

This file defines the command-line representation of soft UID/GID mapping rules. It parses user-provided mapping strings into structured `IdMap` enum variants and formats them back to canonical strings. Runtime conversion into range maps is implemented in `soft_idmap/mod.rs`.

## Main Types

- `IdMap`: command-line mapping rule enum.
- `IdMapError`: parse errors for invalid prefixes, invalid field counts, and invalid numeric values.

`IdMap` variants:

- `Guest { from_guest, to_host, count }`: 1:1 guest-to-host range mapping.
- `Host { from_host, to_guest, count }`: 1:1 host-to-guest range mapping.
- `SquashGuest { from_guest, to_host, count }`: many guest IDs to one host ID.
- `SquashHost { from_host, to_guest, count }`: many host IDs to one guest ID.
- `Bidirectional { guest, host, count }`: symmetric 1:1 range mapping in both directions.
- `ForbidGuest { from_guest, count }`: guest range that should fail when mapped.

## Parsing

`impl FromStr for IdMap` calls `pre_parse()` to split the input into a lowercase prefix and parsed `u32` fields. It then matches the prefix:

- `guest`: expects 3 fields.
- `host`: expects 3 fields.
- `squash-guest`: expects 3 fields.
- `squash-host`: expects 3 fields.
- `forbid-guest`: expects 2 fields.
- `map`: expects 3 fields and creates `Bidirectional`.
- Any other prefix returns `InvalidPrefix`.

`pre_parse()` accepts alphanumeric, `-`, and `_` characters in the prefix. The first other character becomes the separator. All remaining fields are split using that exact separator and parsed as `u32`.

This allows forms like `guest:1:2:3` and also other non-alphanumeric separators, except `-` and `_` cannot be separators because they are allowed in prefixes.

## Formatting

`impl Display for IdMap` emits canonical colon-separated strings:

- `guest:<from_guest>:<to_host>:<count>`
- `host:<from_host>:<to_guest>:<count>`
- `squash-guest:<from_guest>:<to_host>:<count>`
- `squash-host:<from_host>:<to_guest>:<count>`
- `forbid-guest:<from_guest>:<count>`
- `map:<guest>:<host>:<count>`

`IdMapError` also has a human-readable `Display` implementation.

## Integration Points

This module is exported by `soft_idmap/mod.rs`. Parsed `Vec<cmdline::IdMap>` values are consumed by `TryFrom<Vec<cmdline::IdMap>> for soft_idmap::IdMap<Guest, Host>`, which performs range validation, overlap detection, and runtime map construction.

## Important Invariants

- All numeric values are `u32`.
- Prefixes are normalized to lowercase.
- Field count validation happens after numeric parsing.
- Empty input returns an `InvalidLength` error with approximate expected/seen values.
- The parser does not validate range overflow or overlap; that is handled by runtime conversion in `mod.rs`.

## Risks And Edge Cases

- Because field count is checked after parsing, extra empty fields produce `InvalidValue` rather than `InvalidLength`.
- The first non-prefix character chooses the separator, so mixed separators are not accepted as intended.
- `forbid-guest` only expresses guest-to-host failure; there is no command-line host-forbid variant in this file.
