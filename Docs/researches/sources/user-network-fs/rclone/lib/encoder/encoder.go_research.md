# sources/user-network-fs/rclone/lib/encoder/encoder.go

## Purpose
`encoder.go` implements rclone's configurable filename encoder. It translates characters and name patterns that are invalid or problematic on particular storage systems into reversible Unicode-safe representations, and converts names between backend-specific encodings and rclone's standard encoding.

## Important APIs, types, and functions
- `QuoteRune` is the escape marker used when input already contains an encoded-looking rune.
- `MultiEncoder` is a bitmask implementing `Encoder`, `pflag.Value`, and `fmt.Scanner` style parsing.
- `Encode*` constants select character classes: slash, Windows punctuation, quotes, hash/percent, control characters, leading/trailing spaces or periods, invalid UTF-8, dot names, and more.
- Synthetic masks include `EncodeWin` and `EncodeHashPercent`.
- `Encoder` defines `Encode`, `Decode`, `FromStandardPath`, `FromStandardName`, `ToStandardPath`, and `ToStandardName`.
- Alias helpers `alias`, `ValidStrings`, `String`, `Set`, `Type`, and `Scan` provide text configuration.
- `MultiEncoder.Encode` and `MultiEncoder.Decode` implement reversible transformation.
- `appendQuotedBytes` and `appendUnquotedByte` handle invalid UTF-8 byte escaping.
- `Identity`, `FromStandardPath`, `FromStandardName`, `ToStandardPath`, and `ToStandardName` provide generic conversion helpers.

## Control flow
Initialization registers human-readable names for every bitmask. `Set` parses comma-separated names or numeric bit values into a mask. `Encode` short-circuits raw and empty names, handles special dot names, strips at most one configured prefix-only and suffix-only character into encoded prefix/suffix strings, then scans for the first rune needing transformation. It writes unchanged leading bytes, then maps configured ASCII punctuation to fullwidth variants, NUL/control/CR/LF/DEL to symbol-for-control runes, encoded-looking input to `QuoteRune` plus the original rune, and optionally invalid UTF-8 bytes to quoted hex pairs. `Decode` mirrors this flow: it handles dot names, reverses prefix/suffix substitutions, scans for encoded runes, tracks quote state, decodes fullwidth/control symbols back to raw characters unless quoted, and reconstructs invalid UTF-8 bytes when that flag is enabled.

## State and persistence behavior
Package-level alias maps are initialized once and then read. Encoding itself is stateless and deterministic. No filesystem or persistent state is touched; persistence implications appear when encoded names are stored on remotes.

## Dependencies and integration points
The file depends on standard packages `bytes`, `fmt`, `io`, `sort`, `strconv`, `strings`, and `unicode/utf8`. It is a central integration point for rclone backends: each backend advertises or configures an encoder to map remote object names into rclone's standard namespace without collisions.

## Risks and edge cases
Reversibility depends on quote handling being exactly symmetrical for every encoded rune. Prefix and suffix handling intentionally transforms only one leading and one trailing character according to priority, which matters for names with multiple restricted edge characters. Invalid UTF-8 handling is byte-oriented and interacts with Go's `range` replacement-rune behavior. `Set` accepts numeric masks, so users can enable unknown future bits that `String` displays as hex and `Encode` may ignore. Because path conversion splits on `/`, slash encoding must be applied to path components rather than whole already-separated standard paths.

## Test signals
No encoder tests are included in this subset, but comments point to `fstests/fstests/fstests.go` `FsEncoding` coverage. Critical test signals should include encode/decode round trips for every flag, quote collisions, dot names, leading/trailing variants, invalid UTF-8 bytes, and path conversion between `Standard` and backend encoders.
