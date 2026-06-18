# File Research: sources/virtualization/virtiofsd/src/idmap.rs

## Scope

Command-line parsing and formatting for namespace UID/GID map ranges.

## APIs Covered

- `IdMapError`: invalid delimiter, incomplete map, invalid integer.
- `UidMap` and `GidMap` with `FromStr` and `Display`.
- Internal `parse_idmap()`.
- `IdMapSetUpPipeMessage` for setup synchronization.

## Behavior

- Accepts delimiter-wrapped forms such as `:0:100000:65536:`.
- The delimiter is taken from the final character and must be non-alphanumeric.
- Requires an initial matching delimiter and exactly three numeric fields.
- Displays maps back in colon-delimited form.

## Risks

Parsing is deliberately delimiter-flexible but strict about delimiter consistency and field count. These values feed namespace setup in the daemon CLI path.
