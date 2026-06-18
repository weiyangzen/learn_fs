# sources/test-tools/syzkaller/pkg/tool/flags.go

## Purpose

`flags.go` adds common command-line parsing helpers, especially optional flags for compatibility with older binaries and multi-config flag parsing.

## Important APIs, Types, And Functions

`Flag` stores name/value pairs. `OptionalFlags` serializes optional flags into one `-optional=...` argument. `ParseFlags` parses the flag set, deserializes optional flags, applies only those known to the binary, and logs ignored unknown ones. `ParseArchList` validates/sorts target arches. `serializeFlags`, `deserializeFlags`, `flagEscape`, and `flagUnescape` implement a colon/equal-safe encoding. `CfgsFlag` implements `flag.Value`.

## Control Flow, State, Dependencies, And Integration

Parsing mutates the provided `flag.FlagSet` and any registered `CfgsFlag`. The optional flag encoding escapes controls, spaces, non-ASCII, `:`, `=`, and backslash as `\xNN`, making it safe as a single argument. Dependencies include `targets.List` and syzkaller logging.

## Risks And Test Signals

`ParseFlags` registers the `optional` flag on every call, so repeated calls on the same flag set may conflict. `CfgsFlag.Set` rejects multiple invocations and includes empty entries if given empty comma segments. `flags_test.go` and `flags_fuzz.go` cover compatibility parsing, arch validation, escaping, and round trips.
