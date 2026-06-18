# sources/user-network-fs/rclone/fs/bits.go

Purpose: defines a generic bitmask flag option type for rclone settings that can be represented as named choices, parsed from comma-separated strings, scanned, and marshaled to JSON.

Important APIs/types/functions: `Bits[C BitsChoices] uint64` is the flag type. `BitsChoicesInfo` pairs bit values with display names. `BitsChoices` requires `Choices() []BitsChoicesInfo`. Methods include `String`, `Help`, `Choices`, `Set`, `IsSet`, `Type`, `Scan`, `UnmarshalJSON`, and `MarshalJSON`. `Type` supports a custom `Type() string` method on the choices type via the package-level `typer` convention.

Control flow: `String` emits the zero-value choice name when one exists, then emits known nonzero bits in choice order and appends `Unknown-0x...` if unknown bits remain. `Set` splits input on commas, trims spaces, ignores empty parts, case-insensitively matches choice names, ORs matched bits, and only assigns on success. `UnmarshalJSON` delegates to `UnmarshalJSONFlag`, accepting either string flag names or integer values. `MarshalJSON` always serializes the `String` form.

State and persistence behavior: no global state. The parsed bitmask is stored in the `Bits` value. JSON and config persistence use string names by default, while numeric JSON input remains backward-compatible.

Dependencies and integration points: uses `encoding/json`, `fmt`, and `strings`. Integrates with rclone option parsing through `Flagger`, `FlaggerNP`, JSON config, `fmt.Scanner`, and CLI help generation.

Risks: duplicate names or overlapping bits in a choices implementation would create ambiguous output/input. `String` consumes known bits from a local copy, so unknown combined bits are reported as one residual mask. A zero input serializes to an empty string if no zero choice is provided.

Test signals: `bits_test.go` checks interfaces, string/help output, case-insensitive parsing, no mutation on parse error, `IsSet`, scan support, JSON string/numeric input, and JSON output.
