# sources/sync-backup/kopia/repo/jsonencoding/jsonencoding.go

Purpose: provides `jsonencoding.Duration`, a wrapper around `time.Duration` with text/JSON marshal and unmarshal behavior suitable for config files.

Important APIs/types/functions: `Duration`, `MarshalText`, and `UnmarshalText`.

Control flow: marshaling emits the duration's standard string form. Unmarshaling trims whitespace, first attempts `strconv.ParseFloat` and treats numeric values as raw nanoseconds, then falls back to `time.ParseDuration`.

State/persistence behavior: affects serialized configuration and manifest-like JSON that embeds durations. Numeric strings preserve legacy nanosecond-style duration encodings.

Dependencies/integration: used by JSON encoding via `encoding.TextMarshaler`/`TextUnmarshaler` semantics.

Risks/test signals: accepting floats can truncate fractional nanoseconds through `time.Duration(f)`. Error wrapping includes the invalid input. Tests cover string durations, whitespace, underscore numeric literals accepted by `ParseFloat`, and invalid input.
