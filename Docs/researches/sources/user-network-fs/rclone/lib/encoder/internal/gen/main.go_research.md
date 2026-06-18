# sources/user-network-fs/rclone/lib/encoder/internal/gen/main.go

Source read signal: reviewed complete local file (628 lines, sha256 5e9a6832dfe49fcb).

Purpose: Generates `encoder_cases_test.go`, the large fixture table used to verify `MultiEncoder` encode/decode behavior across masks and edge rules.

Important APIs/types/functions: Uses `mapping`, `edge`, `stringPair`, `maskBits`, `allEdges`, `allMappings`, and helpers `invalidMask`, `runeRange`, `getMapping`, `buildTestString`, `buildEdgeTestString`, `fixEdges`, `runePos`, and `quotedToString`.

Control flow: `main` seeds a deterministic RNG, creates `encoder_cases_test.go`, writes test headers, emits single-mask cases from `allMappings`, emits single-edge cases for left/right edge-only encodings, then emits double-edge combinations excluding invalid control-mask overlaps.

State and persistence behavior: The generator writes one Go source file in the encoder package and otherwise keeps transient RNG and fixture slices in memory.

Dependencies and integration points: Imports `github.com/rclone/rclone/lib/encoder` and `fs.Fatal`, plus `slices`, `rand`, and file I/O. It is invoked by go generate comments in the generated file header and must track encoder flag definitions.

Risks and test signals: Generated cases are the main regression net for flag combinations, quote-rune handling, and edge substitutions. Any new encoder flag needs updates to `maskBits` and, if applicable, `allMappings`/`allEdges`; source duplication or syntax drift in this generator would break fixture regeneration.
