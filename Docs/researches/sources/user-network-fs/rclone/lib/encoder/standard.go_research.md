# sources/user-network-fs/rclone/lib/encoder/standard.go

Source read signal: reviewed complete local file (21 lines, sha256 c2ad677dd0847be3).

Purpose: Defines shared encoder presets for rclone's standard path representation, base local-safe representation, and display/logging representation.

Important APIs/types/functions: Constants are `Standard`, `Base`, and `Display`.

Control flow: No runtime flow; these bitmasks are consumed by encoder methods and backends.

State and persistence behavior: No mutable state. `Standard` is part of rclone's internal path contract and can affect stored config/cache names or remote paths when used by backends.

Dependencies and integration points: Depends on `MultiEncoder` flags in the same package. Used by OS-specific policies, backend encoders, and display formatting.

Risks and test signals: Changing presets has broad compatibility impact. Tests should continue to assert slash, zero, delete/control, and dot encoding choices for standard paths.
