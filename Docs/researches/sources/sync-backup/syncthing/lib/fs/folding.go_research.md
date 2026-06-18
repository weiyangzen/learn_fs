# sources/sync-backup/syncthing/lib/fs/folding.go

## Purpose
Provides Unicode lowercasing and NFC normalization for case-insensitive path comparison.

## Important APIs, Types, and Functions
`UnicodeLowercaseNormalized`, `isASCII`, `toLowerASCII`, `toLowerUnicode`, and `firstCaseChange`.

## Control Flow
Fast path returns ASCII lowercase strings unchanged or lowercases only changed ASCII spans. Non-ASCII path finds first rune whose lower(upper(r)) differs, writes prefix unchanged, folds remaining runes, and normalizes to NFC. Special handling avoids simple Latin-1 `µ` pitfalls and uses upper-then-lower folding for OS-like behavior.

## State and Persistence Behavior
Pure string transformation; no state.

## Dependencies and Integration Points
Used by case conflict detection, fakeFS case-insensitive mode, Windows path matching, and mtime case-insensitive keys.

## Risks
Unicode case folding is locale-insensitive and intentionally approximate to filesystem behavior. It does not equate German `ß` with `ss` and chooses one Greek sigma form.

## Test Signals
`folding_test.go` covers ASCII, Latin, Cyrillic, Greek, Turkish, non-cased scripts, Kelvin sign, and NFC renormalization.
