# sources/storage-engines/foundationdb/contrib/ddsketch_conversion.py

## Purpose
CLI utility to convert a numeric value to a DDSketch bucket index or a bucket index back to an approximate value.

## Important APIs, Types, And Functions
Arguments are `--error_guarantee`, `--value`, and `--bucket`. It constructs `ddsketch_calc.DDSketch` and calls `getIndex()` and/or `getValue()`.

## Control Flow
After parsing arguments, default error is `0.005` unless overridden. If `--value` is present it prints the bucket; if `--bucket` is present it prints the representative value. Both can be requested in one invocation.

## State And Persistence
No persistent state. Output is printed to stdout.

## Dependencies And Integration
Imports local `ddsketch_calc` as `dd`. Intended for developers inspecting DDSketch bucket mappings.

## Risks
`--value` is typed as int, so fractional latency values cannot be passed despite the DDSketch math accepting floats. It does not require either `--value` or `--bucket`, resulting in a no-op command. Invalid error guarantees are not validated.

## Test Signals
Exercise value-only, bucket-only, both options, no options, custom error, invalid error, and known round-trip expectations.
