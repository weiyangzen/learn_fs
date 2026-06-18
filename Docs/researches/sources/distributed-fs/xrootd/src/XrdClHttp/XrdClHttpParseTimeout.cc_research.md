# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpParseTimeout.cc

## Purpose

This file implements parsing and formatting of HTTP plugin timeout durations. It accepts a Go-like sequence of numeric values with units and converts them to `timespec`, then marshals `timespec` values back into seconds plus milliseconds.

## Important APIs, types, and functions

`ParseTimeout` recognizes `ns`, `us`, `ms`, `s`, `m`, and `h`, rejects empty strings, negative values, missing units, unknown units, invalid numbers, and out-of-range `stod` values. It treats exact `"0"` as `{0,0}`. `MarshalDuration` emits `"0s"` for zero and otherwise writes `<sec>s<ms>ms`, truncating nanoseconds to milliseconds.

## Control flow

Parsing repeatedly calls `std::stod` on the remaining string, extracts up to two non-digit unit characters, adds scaled seconds/nanoseconds to an accumulator, normalizes nanoseconds over one billion, and advances by the unit length. Errors set `errmsg` and return false.

## State and persistence behavior

The functions are stateless and deterministic except for floating-point rounding/truncation during unit conversion. They do not persist configuration; callers store the parsed values in factory/file static settings.

## Dependencies and integration points

The parser is used by HTTP factory and file configuration paths for settings such as stall timeout, minimum client timeout, and default header timeout. It depends only on standard C/C++ string/time facilities.

## Risks and edge cases

Decimal nanoseconds/microseconds can be truncated by assignment to integer `tv_nsec`. The normalization uses `>` rather than `>=`, so exactly `1,000,000,000` nanoseconds is not normalized until more nanoseconds are added. Unit extraction looks at two non-digit characters, so unexpected alphabetic suffixes produce unknown-unit errors. `MarshalDuration` loses sub-millisecond precision.

## Test signals

Tests should cover valid compound durations (`1h5m`, `30ms`, decimals), `"0"`, missing units, empty input, negative values, unknown units, exact nanosecond normalization boundaries, and marshal precision truncation. No direct tests were found.
