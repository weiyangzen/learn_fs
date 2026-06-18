# sources/object-store/rustfs/crates/utils/src/logging.rs

## Purpose
Provides display/debug masking for access keys or similar secrets before they are written to logs.

## Important APIs, Types, And Functions
`MaskedAccessKey<'a>(pub &'a str)` is a lightweight wrapper. Its `Display` implementation emits an empty string for empty input, `***` for one to four characters, first and last character with `***` for five to eight characters, and first four plus last four with `***` for longer values. `Debug` delegates to `Display`.

## Control Flow And State
The wrapper is stateless and allocates a `Vec<char>` to mask by character count rather than raw byte index, avoiding UTF-8 slicing bugs.

## Dependencies And Integration Points
Uses only `std::fmt` and is always exported from `lib.rs`. It should be used at log call sites that include access keys or derived identifiers.

## Risks And Test Signals
Masking preserves length class and edge characters, so it reduces accidental disclosure but is not anonymization. Very short secrets are fully hidden. Unit tests cover empty, short, medium, long, and `Debug` formatting.
