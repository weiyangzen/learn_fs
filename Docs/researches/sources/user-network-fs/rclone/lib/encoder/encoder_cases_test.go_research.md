# Research: sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009781`: lines 1-4825, `Docs/researches/chunks/subset-b-009781_research.md`
- `subset-b-009782`: lines 4826-9466, `Docs/researches/chunks/subset-b-009782_research.md`
- `subset-b-009783`: lines 9467-14239, `Docs/researches/chunks/subset-b-009783_research.md`
- `subset-b-009784`: lines 14240-18902, `Docs/researches/chunks/subset-b-009784_research.md`
- `subset-b-009785`: lines 18903-23305, `Docs/researches/chunks/subset-b-009785_research.md`
- `subset-b-009786`: lines 23306-27672, `Docs/researches/chunks/subset-b-009786_research.md`
- `subset-b-009787`: lines 27673-32004, `Docs/researches/chunks/subset-b-009787_research.md`
- `subset-b-009788`: lines 32005-36348, `Docs/researches/chunks/subset-b-009788_research.md`
- `subset-b-009789`: lines 36349-40678, `Docs/researches/chunks/subset-b-009789_research.md`
- `subset-b-009790`: lines 40679-41845, `Docs/researches/chunks/subset-b-009790_research.md`

## Chunk Research

### subset-b-009781: lines 1-4825

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 1-4825

## Scope

This chunk covers the opening segment of rclone's generated encoder test-case table. The source begins with the generator notice and package declaration, then defines:

- all of `testCasesSingle`, cases `0` through `19`;
- the beginning of `testCasesSingleEdge`, cases `0` through `1182` complete and the opening of case `1183`.

The assigned range ends inside the `testCasesSingleEdge` literal at line 4825, after the `mask: EncodeZero | EncodeLeftCrLfHtVt` line for case `1183`. Later lines in the same source file continue that case, finish `testCasesSingleEdge`, and define `testCasesDoubleEdge`; those later tables are outside this chunk.

## Purpose

`encoder_cases_test.go` is generated test data for `lib/encoder`. It supplies deterministic `testCase` literals consumed by `encoder_test.go` to verify that `MultiEncoder.Encode` maps restricted filename characters to safe Unicode substitutes and that `MultiEncoder.Decode` reverses the transformation exactly.

This chunk focuses on two classes of coverage:

- Single-mask coverage: each individual character-class flag with a mixed string containing raw characters, already-encoded Unicode equivalents, control bytes, fullwidth characters, and ordinary filler.
- Single-edge coverage: one ordinary encodable mask combined with one left-edge flag, exercising leading-only substitutions while making sure identical characters away from the leading edge are not incorrectly transformed.

The file protects rclone backends that must translate names for storage systems with filename restrictions, especially systems that reject NUL, slash, Windows-reserved punctuation, leading spaces/periods/tildes, control characters, or ambiguous already-encoded forms.

## Important APIs, Types, And Data

The generated data uses the `testCase` type from `encoder_test.go`:

- `mask MultiEncoder`: bitmask selecting encoding behavior.
- `in string`: raw filename input.
- `out string`: expected encoded filename.

The masks referenced in this chunk are `MultiEncoder` constants from `encoder.go`:

- Core printable/control masks: `EncodeZero`, `EncodeSlash`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, `EncodeCrLf`, `EncodeDel`, and `EncodeCtl`.
- Left-edge masks: `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeLeftTilde`, and `EncodeLeftCrLfHtVt`.

The expected outputs demonstrate the encoder's substitution alphabet:

- `QuoteRune` is `‛`; it disambiguates an input that already contains an encoded substitute.
- Many printable ASCII restrictions map to fullwidth equivalents, such as `/` to `／`, `:` to `：`, `?` to `？`, `*` to `＊`, `|` to `｜`, `\` to `＼`, and quotes/brackets/semicolons/exclamation marks to their fullwidth forms.
- NUL maps to `␀`; control characters can map into the Unicode control-picture block such as `␉`, `␊`, `␋`, and `␍`.
- Leading space maps to `␠`, leading period to `．`, leading tilde to `～`, and leading CR/LF/HT/VT to their control-picture forms.

Within lines 1-4825, the mask distribution is systematic: each ordinary encodable mask appears once in `testCasesSingle`, then most ordinary masks are paired with each visible left-edge mask for repeated edge-position cases. The range reaches deeper into `EncodeZero | EncodeLeftCrLfHtVt` than the earlier edge groups and is truncated before that group is complete.

## Control Flow

This file has no executable control flow of its own. It is a package-level set of Go composite literals. Runtime control flow comes from `encoder_test.go`:

1. `TestEncodeSingleMask` iterates over `testCasesSingle`.
2. For each case, it constructs `e := tc.mask`, calls `e.Encode(tc.in)`, and checks the result equals `tc.out`.
3. It then calls `e.Decode(got)` and checks that decoding returns the original `tc.in`.
4. `TestEncodeSingleMaskEdge` repeats the same Encode/Decode round-trip assertion over `testCasesSingleEdge`.

The product control path under test is `MultiEncoder.Encode` and `MultiEncoder.Decode` in `encoder.go`. For edge masks, `Encode` first peels off at most one qualifying prefix, then at most one qualifying suffix, and only then scans the remaining middle string for normal character substitutions. This ordering matters for the cases in this chunk: a leading already-encoded marker such as `␠`, `．`, `～`, or `␊` must be quoted when it sits at the protected edge, but the same rune inside the middle or at the opposite edge should usually remain unchanged unless another selected mask applies.

## State And Persistence Behavior

The chunk is static generated test data. It does not read files, write files, allocate durable state, access environment variables, or persist runtime state. Its only state is the compiled in-memory slices created when Go builds the `encoder` package tests.

The persistence risk is source-level rather than runtime-level: because the file is generated by `lib/encoder/internal/gen/main.go`, manual edits to individual cases can be overwritten by `go generate` and can also create drift between the generator and committed test data.

## Dependencies And Integration Points

Primary integration points:

- `lib/encoder/encoder_test.go`: defines `testCase` and consumes `testCasesSingle` and `testCasesSingleEdge`.
- `lib/encoder/encoder.go`: defines `MultiEncoder`, mask constants, `QuoteRune`, `Encode`, and `Decode`.
- `lib/encoder/internal/gen/main.go`: generator that writes this file. The visible generation logic writes `testCasesSingle`, then `testCasesSingleEdge`, using deterministic random strings and edge-case expansion.
- Backend encoding declarations elsewhere in rclone depend on the same `MultiEncoder` behavior to make remote filenames legal while preserving round-trip identity.

The generated strings intentionally include non-ASCII filler, fullwidth characters, control-picture characters, raw control bytes, DEL/NUL, and already-encoded variants. That gives the tests signal for Unicode handling and quote disambiguation without needing each backend to reproduce these combinations.

## Risks And Maintenance Notes

- The file is generated and very large. Hand-editing individual literals is fragile; generator changes should be preferred when behavior changes.
- Chunk boundaries are not Go-syntax boundaries. This assigned range ends inside case `1183`, so this chunk must be merged with later chunks before treating the source file as a complete table.
- The tests assert exact byte/string outputs. Any change to `QuoteRune`, fullwidth mappings, control-picture mappings, or edge-prefix/suffix priority will cause many failures.
- Edge masks are subtle because they only apply at the beginning or end of a name, while ordinary masks apply throughout the remaining string. Reordering prefix/suffix processing or middle scanning can break cases where the same rune appears at multiple positions.
- Already-encoded forms are deliberately quoted at protected positions. Removing quote behavior would make Decode ambiguous and can lose information for filenames that originally contained fullwidth/control-picture characters.
- The generated cases include raw control bytes and escape sequences in Go string literals. Tooling that normalizes text, rewrites Unicode, or changes escapes could alter test meaning.

## Test Signals

Strong validation signals for this chunk are:

- `go test ./lib/encoder` from the rclone source tree passes `TestEncodeSingleMask` and `TestEncodeSingleMaskEdge`.
- Regenerating with `go generate ./lib/encoder` produces the same case ordering and expected outputs for this range.
- Representative single-mask failures identify the exact mask name and case index, making regressions local to one mapping class.
- Representative edge failures show whether the bug is in leading-space, leading-period, leading-tilde, or leading-CR/LF/HT/VT handling.
- Decode round-trip assertions pass for both raw restricted characters and inputs that already contain their encoded Unicode counterparts.

This chunk's main research signal is that it is not independent business logic; it is a generated oracle for the encoder's reversible filename mapping contract.

### subset-b-009782: lines 4826-9466

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 4826-9466

## Scope

This chunk covers a generated section of `encoder_cases_test.go` inside `testCasesSingleEdge`. The assigned range starts in the tail of case 1183, then covers complete cases 1184 through 2342 and the opening of case 2343. All complete cases in this range combine `EncodeLeftCrLfHtVt` with one ordinary single-character encoder mask.

The visible mask groups are:

- `EncodeZero | EncodeLeftCrLfHtVt`: tail of the generated group, 39 visible complete cases in this chunk.
- `EncodeSlash | EncodeLeftCrLfHtVt`
- `EncodeSingleQuote | EncodeLeftCrLfHtVt`
- `EncodeBackQuote | EncodeLeftCrLfHtVt`
- `EncodeLtGt | EncodeLeftCrLfHtVt`
- `EncodeSquareBracket | EncodeLeftCrLfHtVt`
- `EncodeSemicolon | EncodeLeftCrLfHtVt`
- `EncodeExclamation | EncodeLeftCrLfHtVt`
- `EncodeDollar | EncodeLeftCrLfHtVt`
- `EncodeDoubleQuote | EncodeLeftCrLfHtVt`
- `EncodeColon | EncodeLeftCrLfHtVt`
- `EncodeQuestion | EncodeLeftCrLfHtVt`
- `EncodeAsterisk | EncodeLeftCrLfHtVt`
- `EncodePipe | EncodeLeftCrLfHtVt`
- `EncodeHash | EncodeLeftCrLfHtVt`
- `EncodePercent | EncodeLeftCrLfHtVt`: partial group, ending mid-case at the chunk boundary.

Most complete non-boundary groups in this range contain 76 cases each. The generator emits a dense matrix for each leading CR/LF/HT/VT edge character and for each paired punctuation mapping.

## Purpose

The file is generated regression test data for rclone's `lib/encoder` package. Its purpose is to prove that `MultiEncoder.Encode` and `MultiEncoder.Decode` remain reversible when an edge-only rule is combined with another character mapping.

This chunk specifically validates the leading CR/LF/HT/VT rule. With `EncodeLeftCrLfHtVt`, only a leading tab, newline, vertical tab, or carriage return is rewritten to the matching Unicode control-symbol form:

- tab to `␉`
- newline to `␊`
- vertical tab to `␋`
- carriage return to `␍`

If one of those symbol forms is already present at the start of the name, the encoder prefixes it with `QuoteRune` (`‛`) so decode can distinguish a literal symbol from an encoded control byte. The rest of the name is still processed by the paired mask, such as slash to fullwidth slash or percent to fullwidth percent.

## Important APIs, Types, And Data Shapes

The chunk is data rather than executable logic. Each row is a `testCase` value with:

- `mask MultiEncoder`: bitmask selecting the encoder behavior under test.
- `in string`: raw file name input.
- `out string`: expected encoded file name output.

The consuming type and tests are in `encoder_test.go`. `TestEncodeSingleMaskEdge` iterates `testCasesSingleEdge`, runs `tc.mask.Encode(tc.in)`, compares the result with `tc.out`, then decodes that encoded value and requires the original input.

The implementation being tested is in `encoder.go`:

- `MultiEncoder` is a bitmask type whose flags include `EncodeLeftCrLfHtVt` and the punctuation masks visible in this chunk.
- `QuoteRune` is `‛`, used to disambiguate literal encoded forms from forms produced by `Encode`.
- `MultiEncoder.Encode` handles prefix-only replacements before its main rune scan.
- `MultiEncoder.Decode` reverses prefix-only replacements before decoding the rest of the string.
- `FromStandardName`, `ToStandardName`, `FromStandardPath`, and `ToStandardPath` integrate the same encoder with path/name conversion, although this chunk directly exercises only `Encode` and `Decode`.

The generated cases use mixed ASCII, fullwidth punctuation, Greek letters, control-symbol runes, and escaped control bytes. That mix is intentional: it verifies that the target edge byte is special only at the left edge, while identical bytes or symbol forms in the middle or at the right edge stay literal unless the paired mask also requires conversion.

## Control Flow

Runtime control flow for these cases is simple:

1. `go test` runs `TestEncodeSingleMaskEdge`.
2. The test loops across `testCasesSingleEdge`.
3. For each case, the mask's `Encode` method is called on `in`.
4. The encoded result must exactly equal `out`.
5. The test then calls `Decode` on `out`.
6. Decode must return the original `in`.

Within `Encode`, the important branch for this chunk is the prefix-only block. When `EncodeLeftCrLfHtVt` is set and no earlier left-edge rule has already consumed a prefix, it checks `in[0]` for `\t`, `\n`, `\v`, or `\r`. If found, it moves the encoded symbol into `prefix` and removes the byte from `in`. If the first rune is already `␉`, `␊`, `␋`, or `␍`, it moves `‛` plus that rune into `prefix` and removes the rune from `in`.

After prefix handling, `Encode` scans the remaining body for ordinary mappings. The paired masks in this range drive conversions such as `/` to `／`, `'` to `＇`, `;` to `；`, `!` to `！`, `#` to `＃`, and `%` to `％`. Existing destination characters are quoted when that paired mask is enabled, so a literal fullwidth slash, fullwidth percent, or control-symbol character can survive a decode round trip.

`Decode` performs the inverse prefix handling. A leading `␉`, `␊`, `␋`, or `␍` becomes the corresponding control byte. A leading `‛` followed by one of those symbols becomes the literal symbol. It then decodes the rest of the body according to the same mask.

## State And Persistence Behavior

There is no runtime persistence in this chunk. The table is static generated Go source committed under the rclone source tree. The only state it affects is transient test process memory while `go test` iterates the cases.

The durable source of truth is the generator in `lib/encoder/internal/gen/main.go`. The file header marks `encoder_cases_test.go` as generated by that program. Regeneration rewrites this file from the generator's mask lists, edge definitions, random seed, and string-building helpers.

Because this range is part of a large generated table, line numbers and case numbers are not stable under generator changes. The behavioral contract is the mask combination and edge matrix, not any specific random filler string.

## Dependencies And Integration Points

Primary dependencies and integration points:

- `encoder.go`: defines `MultiEncoder`, `EncodeLeftCrLfHtVt`, all punctuation masks in this chunk, `QuoteRune`, and encode/decode behavior.
- `encoder_test.go`: defines `testCase` and `TestEncodeSingleMaskEdge`, the direct consumer of these rows.
- `lib/encoder/internal/gen/main.go`: generates this data from `allEdges`, `allMappings`, `maskBits`, and `buildEdgeTestString`.
- Go's `testing` package: subtests are named with the numeric table index, so failures point back to generated case numbers such as 1184 or 2327.
- rclone backend code indirectly depends on `lib/encoder` through filesystem name/path encoding. A regression here can surface as remote filename corruption on backends that reject leading control characters or punctuation.

The generator's `allEdges` entry for `EncodeLeftCrLfHtVt` defines the edge originals as `\t`, `\n`, `\v`, and `\r`, with replacements calculated as `␀` plus the same control value. The visible test groups are produced by pairing that edge with each eligible single-character mapping. The generator deliberately skips invalid combinations where `EncodeCtl` or `EncodeCrLf` would overlap with left/right CR/LF/HT/VT edge handling.

## Risks And Maintenance Notes

- The assigned range starts and ends inside generated cases. Chunk-local parsing as standalone Go would fail, but the full file is valid generated Go source.
- Prefix precedence matters. `EncodeLeftCrLfHtVt` only runs if earlier left-edge rules did not set `prefix`. Future changes to left-edge ordering can alter behavior for combined masks.
- Decode correctness depends on quoting. Without `‛` before literal leading `␉`, `␊`, `␋`, or `␍`, decode would turn a literal symbol into an actual control byte.
- Body handling must not apply the left-edge rule away from the first rune. This chunk contains repeated cases with the same CR/LF/HT/VT byte or symbol at interior and trailing positions to catch over-broad replacement logic.
- Ordinary punctuation encoding must still run after prefix extraction. Cases such as `EncodeSlash | EncodeLeftCrLfHtVt` and `EncodePercent | EncodeLeftCrLfHtVt` verify that leading control handling does not short-circuit body mappings.
- Generated data is hard to audit manually. The safer maintenance workflow is to modify `internal/gen/main.go`, regenerate, and inspect representative group boundaries and failing case numbers rather than editing individual rows.
- The strings include raw control bytes, Unicode symbol-for-control characters, and fullwidth characters. Tooling that normalizes Unicode or trims control characters could silently damage these fixtures.

## Test Signals

Strong validation signals for this chunk are:

- `go test ./lib/encoder` passes, especially `TestEncodeSingleMaskEdge`.
- A failure reports the generated table index and shows `Encode(%q)` or `Decode(%q)` mismatches, making the exact row traceable in `encoder_cases_test.go`.
- Representative cases from each group show these invariants:
  - leading `\t`, `\n`, `\v`, or `\r` is replaced by `␉`, `␊`, `␋`, or `␍`;
  - leading `␉`, `␊`, `␋`, or `␍` is quoted as `‛␉`, `‛␊`, `‛␋`, or `‛␍`;
  - the same control byte or symbol away from the first rune is not handled by the left-edge rule;
  - paired punctuation masks still convert and quote their own source/destination runes in the body;
  - `Decode(Encode(in)) == in` for every row.

For regression work, the most useful focused tests are a small table around each leading control byte plus one paired mask with destination quoting, then the full generated `TestEncodeSingleMaskEdge` suite to catch matrix-level interactions.

### subset-b-009783: lines 9467-14239

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 9467-14239

## Scope

This chunk covers generated rows 2344 through 3536 of `testCasesSingleEdge`, a large table of `testCase` fixtures in rclone's encoder package. The file is generated by `lib/encoder/internal/gen/main.go` and marked `DO NOT EDIT`; this range starts in the middle of the `EncodePercent | EncodeLeftCrLfHtVt` block and ends in the `EncodeBackQuote | EncodeRightCrLfHtVt` block, so it is not a standalone Go declaration by itself.

The rows are data, not executable code. Each entry has a `mask MultiEncoder`, an input string, and the expected encoded output. The surrounding test harness in `encoder_test.go` runs every row through `MultiEncoder.Encode` and then verifies that `MultiEncoder.Decode` returns the original input.

## Purpose

The chunk's purpose is regression coverage for single normal encoder masks combined with one edge-only mask. It focuses on filename characters that are only encoded at the left or right edge of a name, while also checking that a second enabled character class is still transformed anywhere in the string.

The important edge masks in this range are:

- `EncodeLeftCrLfHtVt`, for leading tab, line feed, vertical tab, and carriage return.
- `EncodeRightSpace`, for trailing spaces.
- `EncodeRightPeriod`, for trailing periods.
- `EncodeRightCrLfHtVt`, for trailing tab, line feed, vertical tab, and carriage return.

The ordinary masks paired with those edge masks include `EncodeZero`, `EncodeSlash`, `EncodeLtGt`, `EncodeDoubleQuote`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeDollar`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, `EncodeCrLf`, `EncodeDel`, `EncodeCtl`, `EncodeSquareBracket`, `EncodeSemicolon`, and `EncodeExclamation`.

## Important APIs And Data Shapes

The entries use the `testCase` shape from `encoder_test.go`:

```go
type testCase struct {
    mask MultiEncoder
    in   string
    out  string
}
```

The mask values are bitwise combinations of `MultiEncoder` flags from `encoder.go`. In this chunk, the generated rows exercise combinations such as:

- `EncodePercent | EncodeLeftCrLfHtVt`, where percent signs become fullwidth percent signs and leading CR/LF/HT/VT become their Unicode control-symbol forms.
- `EncodeBackSlash | EncodeLeftCrLfHtVt`, where backslashes become fullwidth reverse solidus while leading CR/LF/HT/VT are edge-encoded.
- `EncodeZero | EncodeRightCrLfHtVt`, `EncodeSlash | EncodeRightCrLfHtVt`, `EncodeSingleQuote | EncodeRightCrLfHtVt`, and `EncodeBackQuote | EncodeRightCrLfHtVt`, where only the final CR/LF/HT/VT is edge-encoded unless the character already appears in encoded form, in which case it is quoted with `QuoteRune`.
- Many `Encode* | EncodeRightSpace` and `Encode* | EncodeRightPeriod` rows, where only the final space or period receives the edge transformation while embedded copies remain literal.

The expected output encodes raw restricted characters to compatibility runes such as `／`, `＼`, `％`, `＇`, `｀`, `␠`, `．`, `␉`, `␊`, `␋`, and `␍`. Existing encoded forms at positions that would otherwise be ambiguous are escaped with `QuoteRune`, the single high-reversed-9 quotation mark `‛`.

## Control Flow

There is no runtime control flow inside this chunk; the table is consumed by `TestEncodeSingleMaskEdge`.

The effective test flow is:

1. `TestEncodeSingleMaskEdge` iterates `testCasesSingleEdge`.
2. For each row, it constructs `e := tc.mask`.
3. It calls `e.Encode(tc.in)` and compares the result with `tc.out`.
4. It calls `e.Decode(got)` and requires the decoded value to equal the original `tc.in`.

Inside `MultiEncoder.Encode`, the relevant control flow is prefix/suffix handling before the general rune mapping pass. Prefix handling checks leading space, period, tilde, then CR/LF/HT/VT if no earlier prefix rule matched. Suffix handling checks trailing space, period, then CR/LF/HT/VT if no earlier suffix rule matched. After edge handling removes the transformed prefix or suffix from the working string, the normal per-rune encoder handles the non-edge mask.

## State And Persistence Behavior

The chunk has no mutable runtime state. Its only persistence role is as checked-in generated Go test data. Regeneration rewrites `encoder_cases_test.go` from `internal/gen/main.go`; the row numbering and exact random-looking Unicode strings are generator output, not manually curated examples.

At test time, state is limited to local variables in the subtest loop. The encoder itself is a `uint` bitmask value and does not retain state across calls. The tests do not touch the filesystem, network, environment, or backend configuration.

## Dependencies And Integration Points

Key dependencies and integration points are:

- `lib/encoder/encoder.go`, which defines `MultiEncoder`, the `Encode*` flags, `QuoteRune`, `Encode`, and `Decode`.
- `lib/encoder/encoder_test.go`, which defines `testCase` and `TestEncodeSingleMaskEdge`.
- `lib/encoder/internal/gen/main.go`, which generates `testCasesSingleEdge` from `allEdges`, `maskBits`, `buildEdgeTestString`, and the encoder mappings.
- Go's `testing` package, because every table row becomes a subtest named by its numeric index.
- Unicode compatibility characters and control-symbol code points used as the encoded representation for filesystem-hostile bytes and runes.

The broader integration surface is rclone backend filename encoding. Backends choose combinations of these `MultiEncoder` flags to safely map names for storage systems that reject path separators, Windows-reserved characters, control characters, trailing spaces, trailing periods, or CR/LF/HT/VT at name edges.

## Risks And Maintenance Notes

- Because this is generated data, manual edits are fragile and will be overwritten. Changes should be made in `internal/gen/main.go` or `encoder.go`.
- The file is very large, and chunk boundaries can split logical blocks. Tools should treat this range as a partial table slice, not as parseable standalone Go.
- Edge masks are order-sensitive. The implementation only applies one prefix rule and one suffix rule, so fixtures are important for detecting accidental precedence changes between space, period, tilde, and CR/LF/HT/VT handling.
- Ambiguity handling depends on `QuoteRune`. Rows where the input already contains encoded forms such as `␍`, `␉`, `␊`, `␋`, `␠`, or `．` protect decode round trips from collisions.
- `EncodeCtl` and `EncodeCrLf` are deliberately excluded from combinations with left/right CR/LF/HT/VT by the generator's invalid-mask filtering. This avoids overlapping responsibility for the same characters and should stay aligned with encoder semantics.
- The generated strings include many non-ASCII runes and escaped control bytes. Any tooling that rewrites the file must preserve UTF-8 content and Go string escapes exactly enough for the expected `Decode(Encode(x)) == x` property.

## Test Signals

Strong validation signals for this chunk are:

- `go test ./lib/encoder -run TestEncodeSingleMaskEdge` passes from the rclone source root.
- Representative subtests around this range, such as rows 2344, 2420, 2630, 2820, 3000, 3300, and 3536, continue to encode and decode without mismatch.
- Regenerating with `go generate ./lib/encoder` produces the same `encoder_cases_test.go` when no generator or encoder mapping logic changed.
- Any change to `Encode`, `Decode`, `QuoteRune`, or the `EncodeRight*` and `EncodeLeftCrLfHtVt` flags should be checked against this table because failures here usually mean a round-trip ambiguity or edge-position regression.

### subset-b-009784: lines 14240-18902

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 14240-18902

## Scope

This chunk covers the tail of the generated `testCasesSingleEdge` table and the first entries of the generated `testCasesDoubleEdge` table in `lib/encoder/encoder_cases_test.go`. The file is generated by `lib/encoder/internal/gen/main.go` and is consumed by the encoder package tests in `lib/encoder/encoder_test.go`.

The source range begins inside `testCasesSingleEdge` at case `3537` and runs through line `18902`, ending partway through `testCasesDoubleEdge` case `40`. It does not define new executable logic; its value is the generated fixture matrix that asserts exact `MultiEncoder.Encode` output and `MultiEncoder.Decode` round trips for edge-sensitive filename transformations.

## Purpose

The chunk verifies two related behaviors:

- Single edge masking with `EncodeRightCrLfHtVt` combined with normal character masks. These cases ensure trailing tab, newline, vertical tab, and carriage return are transformed only when they are at the suffix position, while the same characters and their visible symbol forms remain literal or quoted elsewhere as appropriate.
- Multi-edge masking at the start of `testCasesDoubleEdge`, specifically combinations such as `EncodeZero | EncodeLeftSpace | EncodeLeftPeriod`, `EncodeSlash | EncodeLeftSpace | EncodeLeftPeriod`, and other normal masks combined with both leading space and leading period handling.

The cases protect the ambiguity-management contract in the encoder: reserved source characters are mapped to visually similar Unicode alternatives, while already-encoded Unicode alternatives are prefixed with `QuoteRune` (`‛`) when needed so decoding can recover the original string.

## Important APIs, Types, and Data

- `testCase` is defined in `encoder_test.go` with `mask MultiEncoder`, `in string`, and `out string`.
- `testCasesSingleEdge` is the generated table used by `TestEncodeSingleMaskEdge`. This chunk contains cases `3537` through `4660`.
- `testCasesDoubleEdge` is the generated table used by `TestEncodeDoubleMaskEdge`. This chunk contains its opening cases `0` through the beginning of case `40`.
- `MultiEncoder` is the bitmask type under test. Relevant masks in this chunk include:
  - `EncodeRightCrLfHtVt` for trailing `\t`, `\n`, `\v`, and `\r`.
  - Normal character masks including `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, and `EncodeDel`.
  - Edge masks including `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeLeftTilde`, `EncodeRightSpace`, and `EncodeRightPeriod` in the hand-added overlap cases and double-edge opening.
- Encoded substitutes visible in the fixtures include `␊`, `␋`, `␍`, and `␉` for LF, VT, CR, and HT edge forms; fullwidth variants such as `＜`, `＞`, `［`, `］`, `；`, `！`, `＄`, `＂`, `：`, `？`, `＊`, `｜`, `＃`, `％`, `＼`; and `␡` for DEL.
- `QuoteRune` (`‛`) appears whenever the input already contains a value that could be mistaken for an encoded substitute, or where an encoded edge symbol appears at the active edge.

## Control Flow and Generation Model

At runtime, `TestEncodeSingleMaskEdge` iterates over `testCasesSingleEdge`, calls `tc.mask.Encode(tc.in)`, compares the result to `tc.out`, then calls `tc.mask.Decode(got)` and checks it equals `tc.in`. `TestEncodeDoubleMaskEdge` performs the same encode/decode round trip for `testCasesDoubleEdge`.

The source tables are generated rather than manually maintained. In `internal/gen/main.go`, `allEdges` defines left and right edge behaviors. `EncodeRightCrLfHtVt` maps trailing HT/LF/VT/CR to `␉`/`␊`/`␋`/`␍`, and quotes those symbol runes when they occur at the active right edge as input data rather than as encoder output. `buildEdgeTestString` creates 30-rune randomized strings from printable ASCII, fullwidth printables, encodable characters, encoded characters, and Greek letters. The generator then mutates selected positions at the left edge, right edge, and near-edge positions to prove that edge encoding is positional.

The `testCasesSingleEdge` section in this chunk follows that generated pattern:

- Cases `3537` through `3584` continue `EncodeBackQuote | EncodeRightCrLfHtVt`, mixing backquote/fullwidth-backquote behavior with trailing LF/VT/CR handling.
- Cases `3585` onward cover a succession of normal masks with `EncodeRightCrLfHtVt`. Each group confirms the normal mask still applies across the whole string while right-edge CR/LF/HT/VT handling applies only to the final rune.
- Cases `4649` through `4660` are explicit overlap fixtures appended by the generator for short strings such as `"  "`, `".."`, `" ."` and `"a. "`. These are important because left and right edge replacement can consume one or both ends of very short names.
- Line `18739` starts `testCasesDoubleEdge`. The first generated double-edge entries combine a normal mapping mask with `EncodeLeftSpace | EncodeLeftPeriod`, exercising precedence and quoting when the first rune is a leading space replacement candidate and the next rune is a leading period candidate.

## State and Persistence Behavior

There is no mutable persistent state in this chunk. The tables are static Go literals compiled into the encoder test binary. The persistence concern is source-level reproducibility: the file is marked `// Code generated by ./internal/gen/main.go. DO NOT EDIT.` and can be regenerated by `go generate` from the generator seed and mapping definitions.

The tested production state is transient inside `MultiEncoder.Encode`: it may split an input into a `prefix`, middle `in`, and `suffix` before scanning the middle for normal replacements. These fixtures lock down that split behavior by requiring right-edge replacements to happen before the general rune scan and by ensuring decode reverses quoted edge symbols correctly.

## Dependencies and Integration Points

- Depends on the `encoder` package constants and implementation in `encoder.go`, especially `MultiEncoder.Encode`, `MultiEncoder.Decode`, `QuoteRune`, `fullOffset`, and `symbolOffset`.
- Depends on generated fixture construction in `internal/gen/main.go`, including `allEdges`, `allMappings`, `buildEdgeTestString`, `fixEdges`, and `quotedToString`.
- Integrated through `encoder_test.go`:
  - `TestEncodeSingleMaskEdge` validates all single-edge fixtures, including most of this chunk.
  - `TestEncodeDoubleMaskEdge` validates the double-edge fixtures beginning in this chunk.
- The practical consumers are rclone backend filename encodings. The constants tested here are combined into platform/backend policies such as standard/base encodings and OS-specific encodings.

## Risks and Edge Cases

- Edge ordering is subtle. `Encode` handles prefix-only replacements first and suffix-only replacements second; a short string can be affected at both ends. The explicit short overlap cases at `4649`-`4660` guard against regressions where one edge replacement prevents the other.
- `EncodeRightCrLfHtVt` overlaps semantically with `EncodeCrLf` and `EncodeCtl`. The generator excludes invalid combinations where control/CRLF-wide masks would conflict with left/right CRLF/HT/VT edge masks, so this chunk tests the valid right-edge-only path rather than all possible bitmask combinations.
- Quoting is the main correctness risk. Strings containing `␊`, `␋`, `␍`, `␉`, fullwidth punctuation, `␀`, `␡`, or `QuoteRune` must not decode as if they were produced by encoding an unsafe source character unless quoted. Many cases in this chunk distinguish source edge characters from already-encoded symbol characters.
- UTF-8 and byte indexing are relevant because `Encode` checks the first and last byte for ASCII edge characters, then uses UTF-8 rune decoding for already-encoded symbols. These cases mix ASCII controls, multi-byte Unicode symbols, fullwidth characters, and Greek filler to catch boundary mistakes.
- The data is generated and voluminous. Manual edits to individual expected strings are high risk because the tables encode a matrix invariant, not isolated examples.

## Test Signals

The strongest test signal is round-trip coverage: every fixture asserts both exact encoded output and `Decode(Encode(input)) == input`. For this chunk, meaningful signals include:

- Trailing LF/VT/CR/HT source bytes become `␊`/`␋`/`␍`/`␉` only at the right edge.
- The same visible symbol runes at the right edge become quoted, for example `‛␊`, `‛␋`, `‛␍`, or `‛␉`.
- Normal character mappings still apply independently of the right-edge rule, e.g. `<`/`>` become `＜`/`＞`, `;` becomes `；`, `\` becomes `＼`, `%` becomes `％`, and DEL becomes `␡`.
- Literal encoded forms for normal mappings are quoted when the corresponding mask is enabled, preserving reversibility.
- Very short names with simultaneous edge masks produce deterministic results: `" "` under left and right space encodes to `␠`, `"  "` to `␠␠`, `"..."` under left and right period to `．.．`, and mixed right-period/right-space inputs choose the actual final edge class.

## Research Notes

This chunk is best understood as generated regression data for `MultiEncoder` edge precedence. It does not introduce APIs, but it is part of the encoder package's behavioral contract. When changing `Encode`, `Decode`, mask constants, or the generator, failures in this chunk likely indicate a change in positional edge semantics or quote disambiguation rather than random fixture churn.

### subset-b-009785: lines 18903-23305

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 18903-23305

## Scope

This chunk covers a slice of the generated `testCasesDoubleEdge` table in `lib/encoder/encoder_cases_test.go`. The file is generated by `lib/encoder/internal/gen/main.go` and carries the `//go:generate go run ./internal/gen/main.go` directive, so the table is golden test data rather than hand-maintained implementation.

The requested range starts inside case 40: line 18903 is the `out` field for `EncodeColon | EncodeLeftSpace | EncodeLeftPeriod`, while that case's `mask` and `in` fields are just before the range. It ends inside case 1141: line 23305 is only the `mask` field for `EncodeSquareBracket | EncodeLeftPeriod | EncodeLeftCrLfHtVt`, while that case's `in` and `out` fields follow the range. The complete cases wholly inside the requested range are cases 41 through 1140, with the adjacent fragments needed to understand the chunk boundary.

The complete cases in this range exercise `MultiEncoder.Encode` and `MultiEncoder.Decode` for three-way masks composed of:

- one ordinary mapping flag, such as `EncodeZero`, `EncodeSlash`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDoubleQuote`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeDollar`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, `EncodeCrLf`, `EncodeDel`, or `EncodeCtl`;
- two edge-position flags, mostly combinations of `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeLeftTilde`, `EncodeLeftCrLfHtVt`, `EncodeRightSpace`, `EncodeRightPeriod`, and `EncodeRightCrLfHtVt`.

Within the requested lines there are 1,100 complete `testCase` entries, plus the opening/closing partial case fragments described above. The range is dominated by leading-edge combinations first, then right-edge combinations, then leading control-whitespace combinations.

## Purpose

The chunk is a regression corpus for edge-sensitive filename encoding. It verifies that rclone's encoder can combine a normal character-class transformation with two positional transformations without losing reversibility. Examples include:

- encoding a leading ASCII space to `SYMBOL FOR SPACE` while leaving an ordinary internal or trailing space unchanged unless a right-edge flag applies;
- encoding a leading `.` to `FULLWIDTH FULL STOP` only at the left edge and quoting an input that already starts with the encoded form;
- encoding a leading `~` to fullwidth tilde under `EncodeLeftTilde`;
- encoding leading or trailing tab, newline, vertical tab, and carriage return to the corresponding Unicode control-symbol runes under `EncodeLeftCrLfHtVt` or `EncodeRightCrLfHtVt`;
- applying the selected ordinary mapping in the body, for example `/` to fullwidth slash, `[`/`]` to fullwidth brackets, `*` to fullwidth asterisk, `0x7f` to `SYMBOL FOR DELETE`, or `0x00` to `SYMBOL FOR NULL`;
- preserving literal fullwidth/control-symbol inputs by prefixing them with `QuoteRune` when they would otherwise be ambiguous with encoder output.

This is not production control flow. Its job is to make the implementation's table-driven tests fail if a future encoder change mishandles precedence, quoting, or round-trip behavior when multiple mask bits are enabled together.

## Important APIs, Types, And Functions

The table uses the `testCase` struct from `encoder_test.go`:

- `mask MultiEncoder`: the bitmask under test.
- `in string`: raw filename/name input.
- `out string`: expected encoded output.

The relevant production type is `MultiEncoder` in `encoder.go`. It implements the `Encoder` interface with `Encode`, `Decode`, `FromStandardPath`, `FromStandardName`, `ToStandardPath`, and `ToStandardName`. This chunk directly feeds only `Encode` and `Decode`.

Important constants covered by the chunk:

- `QuoteRune`: the high reversed comma rune used to disambiguate an input rune that already equals an encoded representation.
- `fullOffset`: used by printable ASCII mappings to create fullwidth forms.
- `symbolOffset`: used by NUL/control mappings to create Unicode control-symbol forms.
- edge flags: `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeLeftTilde`, `EncodeLeftCrLfHtVt`, `EncodeRightSpace`, `EncodeRightPeriod`, `EncodeRightCrLfHtVt`.
- ordinary mapping flags: all of the core filename-restriction masks except `EncodeInvalidUtf8` and `EncodeDot` appear in this chunk. `EncodeCtl` and `EncodeCrLf` combinations are intentionally absent when paired with left/right control-whitespace edge flags because the generator's `invalidMask` excludes overlapping control-space semantics.

The generator functions explaining the table shape are:

- `allEdges`: enumerates positional source/replacement pairs for left and right edge-sensitive characters.
- `allMappings`: enumerates ordinary source/replacement rune mappings.
- `buildEdgeTestString`: creates 30-rune randomized but deterministic inputs from printable, fullwidth, encodable, encoded, and Greek filler sets.
- `fixEdges`: rewrites expected output only when an edge rune is actually at the first or last position, and sets quote markers when the input already contains the replacement rune at an encoded edge.
- `invalidMask`: skips ambiguous combinations involving `EncodeCtl` or `EncodeCrLf` with control-whitespace edge flags.

## Control Flow Exercised

`TestEncodeDoubleMaskEdge` iterates over `testCasesDoubleEdge`. For each case it:

1. assigns `tc.mask` to `e`;
2. calls `e.Encode(tc.in)` and expects exact equality with `tc.out`;
3. calls `e.Decode(got)` and expects to recover `tc.in`.

The implementation path in `MultiEncoder.Encode` is important:

1. `EncodeRaw` and empty input return immediately.
2. `EncodeDot` whole-name special cases are skipped for this chunk because `EncodeDot` is not part of these masks.
3. Prefix-only replacements run before suffix-only replacements. `EncodeLeftSpace` has first priority, followed by `EncodeLeftPeriod`, `EncodeLeftTilde`, and `EncodeLeftCrLfHtVt`, each guarded by `prefix == ""`.
4. Suffix-only replacements run on the remaining string and similarly use first-match behavior: right space, then right period, then right control whitespace.
5. If no prefix or suffix was changed, the code searches for the first rune likely to need ordinary mapping. If an edge was changed, it starts the main scan at the beginning of the remaining string, preserving edge edits while still applying body mappings.
6. The main encoding loop maps raw restricted runes to encoded forms and quotes encoded-form input runes with `QuoteRune`.
7. The encoded suffix is appended at the end.

`MultiEncoder.Decode` mirrors this:

1. It first decodes/unwraps a positional prefix if the enabled edge mask matches the leading encoded rune or quoted encoded rune.
2. It then decodes/unwraps a positional suffix if the enabled right-edge mask matches the trailing encoded rune or quoted encoded rune.
3. It scans the body for encoded ordinary mappings and quote sequences.
4. It writes the decoded suffix after the body.

The chunk is especially sensitive to the `prefix == ""` and `suffix == ""` precedence rules. A name beginning with a space and period under `EncodeLeftSpace | EncodeLeftPeriod` should encode only the leading space as the prefix; the period immediately after it is no longer the first rune and remains ordinary data unless another mapping applies. The generated cases repeatedly place original and replacement runes at positions 0, 1, `len-2`, and `len-1` to catch these distinctions.

## State And Persistence Behavior

There is no runtime persistence in this chunk. It is static, generated Go test data checked into the repository. Test execution allocates local strings and buffers only.

The persistent behavior to watch is source maintenance: edits should normally happen in `lib/encoder/internal/gen/main.go` followed by regeneration of `encoder_cases_test.go`, not by manual editing of the generated table. The generator uses a deterministic seed defaulting to `42`, so the corpus is expected to be stable across regeneration unless the generator, mask order, mapping sets, or Go formatting behavior changes.

Because these cases are checked into source control, generator changes can create large diffs. The source line range also starts and ends mid-case, so chunk-level review must not assume this slice is syntactically standalone.

## Dependencies And Integration Points

Primary local dependencies:

- `lib/encoder/encoder.go`: implements `MultiEncoder.Encode` and `MultiEncoder.Decode`, including prefix/suffix handling, ordinary mappings, quoting, invalid UTF-8 byte handling, and path conversion helpers.
- `lib/encoder/encoder_test.go`: defines `testCase` and the `TestEncodeDoubleMaskEdge` harness consuming this table.
- `lib/encoder/internal/gen/main.go`: generates this table from `allEdges`, `allMappings`, and deterministic randomized filler data.
- `lib/encoder/standard.go` and `os_*.go`: define common encoding profiles that rely on the same `MultiEncoder` semantics. This chunk does not test those profiles directly, but the same flags are used by `Standard`, `Base`, `Display`, and platform `OS` encoders.

External dependencies are minimal for this chunk: ordinary Go test execution is enough. The generator imports rclone's `fs` package for fatal logging, but generated test execution does not need external services.

Integration significance:

- Backends that encode remote object names through `MultiEncoder` depend on these edge rules to preserve names that local filesystems or cloud APIs reject.
- The `FromStandardName`/`ToStandardName` and path conversion helpers depend on `Encode`/`Decode` being true inverses at the filename component level.
- Platform-specific encoders, especially Windows and macOS profiles, rely on quoting to distinguish user-supplied fullwidth/control-symbol characters from characters created by encoding.

## Risks And Maintenance Notes

- The table is generated and very large. Manual edits are high-risk because a single literal mismatch can break either exact `Encode` expectations or the `Decode(Encode(in)) == in` round trip.
- The range starts and ends mid-case. Merge/reconciliation tooling should use the surrounding complete file, not this chunk alone, for syntax-aware conclusions.
- Edge precedence is intentionally asymmetric: only one left-edge transformation and one right-edge transformation are applied. Changing that would invalidate many expected outputs in this range.
- `EncodeLeftSpace | EncodeLeftPeriod` and similar left-left combinations do not mean "encode every leading special rune"; they mean "apply the first matching left-edge rule at the current first rune." Cases with `" ."` and `". "`-style layouts protect that behavior.
- `EncodeRightPeriod | EncodeRightSpace` has order-sensitive behavior because right-space detection runs before right-period detection. Although this particular chunk pairs ordinary mappings with right edge flags more often than pure right-right pairs, the same suffix machinery is exercised.
- Quoting is a central safety property. Inputs containing an already encoded form such as `FULLWIDTH FULL STOP`, fullwidth brackets, or `SYMBOL FOR SPACE` must be quoted when that rune sits in a position or character class the mask owns. Otherwise decode would corrupt a literal user filename.
- Control characters are easy to misclassify. The generator deliberately excludes masks that combine `EncodeCtl`/`EncodeCrLf` with left/right control-whitespace edge flags, because tab/newline/vertical-tab/carriage-return overlap with control character handling. Future changes to `invalidMask` should be reviewed against these omissions.
- The corpus includes many non-ASCII runes and escaped bytes. Test failures can be hard to inspect visually; `%q` output from the harness is important for distinguishing raw bytes, fullwidth forms, and quoted encoded forms.

## Test Signals

Useful checks for this chunk:

- `go test ./lib/encoder` from the rclone source tree should run `TestEncodeDoubleMaskEdge` and exercise the cases in this range.
- Regenerate `encoder_cases_test.go` with `go generate ./lib/encoder` and compare the file when generator logic changes.
- If `Encode` prefix/suffix logic changes, inspect failures around combinations of `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeLeftTilde`, `EncodeLeftCrLfHtVt`, `EncodeRightSpace`, `EncodeRightPeriod`, and `EncodeRightCrLfHtVt`.
- If ordinary mappings change, verify representative case groups for `EncodeZero`, `EncodeSlash`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeAsterisk`, `EncodeBackSlash`, `EncodeDel`, and `EncodeCtl`, because this chunk pairs them with edge behavior and quoting.
- Watch both assertions in `TestEncodeDoubleMaskEdge`: an implementation can still produce the expected `out` for some cases while breaking `Decode`, especially if quote handling changes.

No tests were run for this research task; the work here is static source analysis of the requested generated test-data range.

### subset-b-009786: lines 23306-27672

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 23306-27672

## Scope

This chunk is a generated segment of `testCasesDoubleEdge`, the large table consumed by `TestEncodeDoubleMaskEdge` in `lib/encoder/encoder_test.go`. The exact slice starts at the tail of case 1141, contains complete generated cases 1142 through 2232, and ends with the delimiter that opens case 2233. The substantive cases in this span exercise `MultiEncoder.Encode` and `MultiEncoder.Decode` round-trips for combinations of one ordinary character-mapping flag plus two edge-only flags.

## Purpose

The table verifies that edge encoders only affect the configured leading or trailing position while ordinary encoders continue to map or quote their characters across the non-edge body of the filename. In this chunk, the dominant edge focus shifts from leading period to leading tilde:

- `EncodeLeftPeriod` maps a leading `.` to `．` and quotes an already encoded leading `．` as `‛．`.
- `EncodeLeftTilde` maps a leading `~` to `～` and quotes an already encoded leading `～` as `‛～`.
- `EncodeLeftCrLfHtVt` maps only leading tab, line feed, vertical tab, and carriage return to the matching Unicode control-symbol runes.
- `EncodeRightSpace`, `EncodeRightPeriod`, and `EncodeRightCrLfHtVt` are paired with `EncodeLeftPeriod` in the middle of the chunk to prove independent prefix/suffix handling.

The generated strings deliberately include random fullwidth characters, Greek letters, ASCII punctuation, NUL bytes, DEL bytes, control characters, and pre-encoded Unicode forms. That mix makes each case a regression signal for both collision avoidance and reversibility.

## Important APIs, Types, and Functions

- `type MultiEncoder uint` is the bitmask under test. Each `mask:` expression in this chunk combines flags such as `EncodeSquareBracket | EncodeLeftPeriod | EncodeLeftCrLfHtVt`.
- `type testCase struct { mask MultiEncoder; in string; out string }` defines each generated fixture.
- `MultiEncoder.Encode(string) string` is expected to transform `in` into `out`.
- `MultiEncoder.Decode(string) string` is expected to invert `out` back to `in`.
- `TestEncodeDoubleMaskEdge` iterates over `testCasesDoubleEdge`, calling both `Encode` and `Decode` for every case.
- `internal/gen/main.go` owns generation. Its `allEdges` table defines the edge mappings, and the `buildEdgeTestString` path creates both edge-position and non-edge-position variants.

## Case Coverage in This Chunk

The complete cases in this slice cover 1091 mask entries. The first covered group finishes the `EncodeSquareBracket | EncodeLeftPeriod | EncodeLeftCrLfHtVt` block, checking square bracket quoting/mapping while a leading period and leading CR/LF/HT/VT compete for prefix ownership.

The next major groups pair `EncodeLeftPeriod | EncodeLeftCrLfHtVt` with ordinary mapping flags:

- `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, and `EncodeDel`.
- These groups show that if `.` is the first character, `EncodeLeftPeriod` wins and the subsequent tab/newline/vertical-tab/carriage-return remains body content. If the first rune is already `．`, the output is quoted as `‛．`.
- Body characters still follow their ordinary flag rules, for example `]` to `］`, `%` to `％`, `*` to `＊`, `|` to `｜`, DEL to `␡`, and pre-encoded counterparts quoted with `‛`.

The middle section pairs `EncodeLeftPeriod` with right-edge encoders:

- With `EncodeRightSpace`, trailing ASCII space becomes `␠` and trailing `␠` is quoted, while an interior or non-leading period is unchanged.
- With `EncodeRightPeriod`, only the final `.` becomes `．`; final `．` is quoted. The leading-period mapping remains independent.
- With `EncodeRightCrLfHtVt`, trailing tab, line feed, vertical tab, and carriage return become their control-symbol forms, while pre-encoded trailing symbols are quoted.

The latter section switches to `EncodeLeftTilde`:

- `EncodeLeftTilde | EncodeLeftSpace` and `EncodeLeftTilde | EncodeLeftPeriod` verify edge precedence. The encoder implementation processes left-space first, then left-period, then left-tilde only if no earlier prefix was taken. The cases confirm that a leading space or period can consume the prefix slot and leave a following `~` unchanged.
- `EncodeLeftTilde | EncodeLeftCrLfHtVt` exercises the same precedence with leading tab/newline/vertical-tab/carriage-return. Cases beginning with `~` map to `～`; cases beginning with `～` quote to `‛～`; cases where the tilde appears after a control character leave the tilde as non-edge content.
- Ordinary flags paired with `EncodeLeftTilde` include `EncodeZero`, `EncodeSlash`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, `EncodeCrLf`, `EncodeDel`, and `EncodeCtl` depending on the edge-pair family.

## Control Flow

At test runtime, `TestEncodeDoubleMaskEdge` performs a linear table walk. For each row, the mask is assigned to `e`, `e.Encode(tc.in)` must equal `tc.out`, and then `e.Decode(got)` must equal the original input. Failures identify the table index in a subtest name.

At encoder runtime, the relevant `Encode` control flow is:

1. Return unchanged for `EncodeRaw` or empty input.
2. Handle special `EncodeDot` names, which this chunk does not directly target.
3. Build a `prefix` by testing left-edge flags in fixed order: left space, left period, left tilde, then left CR/LF/HT/VT. Only one prefix edge transform is applied because each later edge check requires `prefix == ""`.
4. Build a `suffix` by testing right-edge flags in fixed order: right space, right period, then right CR/LF/HT/VT.
5. If no prefix or suffix was applied, find the first body rune that needs encoding. If a prefix or suffix exists, skip this early no-op optimization and scan the remaining body.
6. Emit the prefix, encoded body, and suffix. Body encoding handles NUL, quote rune, fullwidth collision quoting, control-symbol collision quoting, and each enabled ordinary flag.

This chunk specifically stresses steps 3 and 4, especially the single-prefix rule and independence between prefix and suffix processing.

## State and Persistence Behavior

There is no runtime persistence, filesystem mutation, or global state modified by these cases. The source file itself is generated and deterministic from `internal/gen/main.go` using a fixed default random seed. The only state exercised by tests is local per-case string transformation state: selected prefix, selected suffix, and the body scan buffer inside `MultiEncoder.Encode`; `Decode` must reconstruct the original input without consulting external state.

## Dependencies and Integration Points

- Depends on the encoder package constants and `MultiEncoder` implementation in `lib/encoder/encoder.go`.
- Integrated into Go tests through `encoder_cases_test.go` and `encoder_test.go`; because both files are in package `encoder`, the unexported `testCase` type and generated variables are directly visible.
- Generated by `lib/encoder/internal/gen/main.go`; manual edits would be overwritten by `go generate`.
- The broader rclone integration is filename normalization for backends with restrictive file-name rules. These edge rules protect platforms that reject leading/trailing whitespace, periods, tildes, or control characters while preserving reversibility.

## Risks and Invariants

- Edge precedence is an invariant: only one left-edge transformation may occur. Reordering `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeLeftTilde`, or `EncodeLeftCrLfHtVt` would change outputs in this chunk.
- Prefix and suffix logic must not accidentally encode interior occurrences of edge-only characters. Many cases place `.`, `~`, `．`, `～`, spaces, and control-symbol runes near but not at the relevant edge.
- Collision quoting is critical. Existing encoded forms such as `．`, `～`, `␠`, control-symbol runes, and fullwidth punctuation must be prefixed with `QuoteRune` when the active flag would otherwise make encoded and raw names ambiguous.
- Ordinary mappings must still run when an edge prefix or suffix was already consumed. The body scan path after prefix/suffix selection is therefore covered by combinations like left-period plus square bracket or left-tilde plus percent.
- The generated table is large and easy to desynchronize from `encoder.go`; changes to mappings, mask names, or edge precedence require regenerating this file and reviewing the whole generated diff.
- This chunk begins and ends on generated table boundaries rather than semantic boundaries, so merge/reconciliation should account for case 1141 and case 2233 being split across adjacent chunks.

## Test Signals

Strong test signal comes from round-trip assertions over randomly mixed strings and explicit edge placements. A failure in this chunk usually points to one of these behaviors:

- `EncodeLeftPeriod` or `EncodeLeftTilde` no longer maps or quotes only the first rune.
- `EncodeLeftCrLfHtVt` or `EncodeRightCrLfHtVt` mishandles one of tab, newline, vertical tab, or carriage return.
- Right-edge encoders accidentally run before, instead of after, left-edge trimming of the working string.
- Body mappings are skipped when a prefix or suffix was present.
- `Decode` cannot distinguish raw fullwidth/control-symbol input from encoded output because quote handling changed.

The direct validation command for this source area is:

```bash
cd sources/user-network-fs/rclone
go test ./lib/encoder
```

### subset-b-009787: lines 27673-32004

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 27673-32004

## Chunk Scope

This chunk covers generated Go test data in `encoder_cases_test.go`, specifically a middle slice of the `testCasesSingleEdge` table. The table is generated by `./internal/gen/main.go` and is consumed by `TestEncodeSingleMaskEdge` in `encoder_test.go`. The researched line range contains 1,083 `testCase` entries, numbered roughly `2234` through `3316`, each with a `mask MultiEncoder`, an input string, and the expected encoded output string.

The chunk is data-only: it does not define functions, methods, exported APIs, or package-level control flow beyond extending the `testCasesSingleEdge` slice literal. Its importance is that it forms a dense regression corpus for rclone's `lib/encoder` escaping behavior around leading/trailing edge characters and reserved-character encodings.

## Purpose

The cases validate that `MultiEncoder.Encode` and `MultiEncoder.Decode` remain inverse-safe for combinations of:

- a single primary encoding flag such as `EncodeZero`, `EncodeSlash`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, `EncodeCrLf`, `EncodeDel`, or `EncodeCtl`;
- edge-position flags such as `EncodeLeftTilde`, `EncodeLeftCrLfHtVt`, `EncodeLeftSpace`, `EncodeLeftPeriod`, `EncodeRightSpace`, `EncodeRightPeriod`, and `EncodeRightCrLfHtVt`;
- pre-existing encoded-looking Unicode replacement glyphs such as `␀`, `␉`, `␊`, `␍`, `␡`, fullwidth punctuation, and the escape marker `‛`.

The range starts inside `EncodeDel | EncodeLeftTilde | EncodeLeftCrLfHtVt`, continues through the `EncodeLeftTilde` cross-products with right-space, right-period, and right-CR/LF/HT/VT edge policies, then transitions into `EncodeLeftCrLfHtVt` cross-products with left-space, left-period, left-tilde, right-space, right-period, and right-CR/LF/HT/VT policies. The visible rows prove both ordinary character substitution and collision escaping when an input already contains the encoded form.

## Important APIs, Types, And Data

The table entries use `testCase`, defined in `encoder_test.go` as:

```go
type testCase struct {
    mask MultiEncoder
    in   string
    out  string
}
```

The `mask` values are bitwise combinations of `MultiEncoder` flags. The test harness sets `e := tc.mask`, calls `e.Encode(tc.in)`, compares that value to `tc.out`, then decodes the encoded output and requires the original input to be recovered. This makes every row a two-way contract: exact forward encoding plus decode round-trip.

Important data patterns in this chunk:

- `EncodeLeftTilde` rows distinguish a literal leading `~` from a leading fullwidth `～`; literal leading `~` becomes `～`, while leading `～` is prefixed with `‛` to avoid decode ambiguity.
- `EncodeLeftCrLfHtVt` rows cover leading tab, newline, vertical tab, and carriage return. At the left edge these become visible control pictures such as `␉`, and pre-existing leading `␉`-style values are escaped with `‛`.
- `EncodeRightCrLfHtVt` rows cover trailing tab/newline/vertical-tab/carriage-return. At the right edge raw trailing controls become visible equivalents, while pre-existing visible equivalents are escaped.
- `EncodeRightSpace` and `EncodeRightPeriod` rows validate that only trailing spaces or periods are treated as edge hazards; identical-looking interior characters remain unchanged except when another primary mask applies.
- Primary masks still apply in the middle of edge-policy rows: examples include ASCII `/` to `／`, quote to `＂`, question/fullwidth question disambiguation, `#` to `＃`, `%` to `％`, backslash to `＼`, DEL to `␡`, and NUL to `␀` where the relevant mask or always-on collision behavior requires it.

## Control Flow And Execution

There is no runtime branching in this file chunk. Control flow is provided by `TestEncodeSingleMaskEdge`:

1. Iterate over `testCasesSingleEdge` with the table index as the subtest name.
2. Convert `tc.mask` to the encoder under test.
3. Call `Encode(tc.in)` and compare byte-for-byte against `tc.out`.
4. Call `Decode(got)` and compare byte-for-byte against `tc.in`.

The table order is meaningful for diagnostics because failing subtests report the numeric table index. The inline comments (`// 2234` through about `// 3316` in this chunk) align generated case numbers with subtest names and generator order.

## State And Persistence

The chunk has no mutable state, persistence, IO, goroutines, caches, or side effects. It is compiled into the Go test binary as static string data. State behavior under test belongs to the encoder implementation, not this file: specifically, whether `Encode` can transform reserved or edge-sensitive characters while preserving enough escape information for `Decode` to restore the original string.

The persistence-relevant signal is compatibility of encoded remote names. rclone's encoder behavior affects filesystem object names, so changes to these expected outputs can indicate a backward-compatibility change in how stored or remote paths are represented.

## Dependencies And Integration Points

Direct dependencies visible from this chunk:

- `MultiEncoder` and its bit flags from `lib/encoder/encoder.go`.
- `Encode` and `Decode` methods on `MultiEncoder`.
- The local `testCase` type and `TestEncodeSingleMaskEdge` harness in `encoder_test.go`.
- The generator `lib/encoder/internal/gen/main.go`, referenced by the file header and `go:generate`, which owns regeneration of this data.

Integration points:

- The table is part of the `encoder` package tests and runs with `go test ./lib/encoder` or wider rclone test commands.
- Backend-specific encoders in rclone rely on these low-level transformations to map provider-restricted names to safe remote names and back.
- The generated corpus complements smaller hand-readable tests by exercising collision behavior across many Unicode, ASCII punctuation, and control-character contexts.

## Risks And Edge Cases

- Because this file is generated, manual edits to one row are fragile and will be overwritten by `go generate`. Correct fixes should usually be made in the encoder implementation or generator input logic.
- The table is large and repetitive; a bad generator change can create many internally consistent but semantically wrong expectations. Review should focus on representative patterns and the generator logic, not only on row count.
- Escape collision behavior is subtle. Inputs containing already-encoded glyphs such as `␉`, `␀`, `␡`, fullwidth punctuation, or leading `～` must be escaped with `‛` in contexts where decode would otherwise collapse distinct original names.
- Edge policies are position-sensitive. Rows in this chunk deliberately include the same character at the left edge, right edge, and interior positions to catch accidental "encode everywhere" or "encode nowhere" regressions.
- Right-edge CR/LF/HT/VT cases include multi-character contexts with both interior and trailing controls. Implementations that trim, normalize, or process runes without preserving position could pass some central replacements but fail these rows.
- Several rows mix ASCII controls, Unicode control pictures, fullwidth variants, and the escape prefix in the same string. Any change in UTF-8 iteration, rune width assumptions, or replacement table ordering can break round-trip safety.

## Test Signals

Primary test signal: `TestEncodeSingleMaskEdge` must pass for every entry in this span. For each row, failure can happen in two ways:

- `Encode(tc.in)` differs from the generated expected `tc.out`, indicating a forward mapping or edge-position regression.
- `Decode(got)` differs from `tc.in`, indicating a collision, unescape, or inverse-mapping regression.

The most useful diagnostic is the subtest number. In this chunk:

- around `2234-2399`, failures point at `EncodeLeftTilde` interactions with left CR/LF/HT/VT, right-space, and right-period behavior;
- around `2400-2671`, failures point at `EncodeLeftTilde | EncodeRightCrLfHtVt` combinations;
- around `2672-2759`, failures point at `EncodeLeftCrLfHtVt | EncodeLeftSpace`;
- around `2760-2831`, failures point at `EncodeLeftCrLfHtVt | EncodeLeftPeriod`;
- around `2832-2911`, failures point at `EncodeLeftCrLfHtVt | EncodeLeftTilde`;
- around `2912-2959`, failures point at `EncodeLeftCrLfHtVt | EncodeRightSpace`;
- around `2960-3047`, failures point at `EncodeLeftCrLfHtVt | EncodeRightPeriod`;
- around `3048-3316`, failures point at `EncodeLeftCrLfHtVt | EncodeRightCrLfHtVt`.

## Research Notes For Merge Lane

This chunk should be merged as a generated-data slice of `testCasesSingleEdge`, not as independent executable code. The final per-file research should combine it with adjacent chunks to explain the whole generated file structure: `testCasesSingle`, `testCasesSingleEdge`, and later generated edge/cross-product tables. For this chunk specifically, preserve the point that its main coverage is edge-position interactions and decode collision prevention for control pictures, fullwidth characters, and the `‛` escape marker.

### subset-b-009788: lines 32005-36348

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 32005-36348

## Scope

This chunk covers lines 32005-36348 of the generated Go test fixture `sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go`. The range is inside `var testCasesSingleEdge = []testCase{...}` and contains 1,086 generated `testCase` entries, numbered 3317 through 4402. It starts in the middle of the `EncodeBackSlash | EncodeLeftCrLfHtVt | EncodeRightCrLfHtVt` group and ends in the early `EncodeSingleQuote | EncodeRightPeriod | EncodeLeftTilde` group; the surrounding file continues the same generated matrix before and after this slice.

The file header says it is generated by `./internal/gen/main.go` and should not be edited manually. This chunk is data, not executable logic, but it is part of the package's table-driven test surface for the `encoder.MultiEncoder` implementation.

## Purpose

The chunk supplies edge-position encoding fixtures for rclone's filename encoder. Each row describes:

- `mask`: a `MultiEncoder` bitmask combining one normal character-class encoding with one or two edge-only encodings.
- `in`: a raw input filename-like string.
- `out`: the exact string expected from `mask.Encode(in)`.

The corresponding test harness also decodes `out` and requires the original `in`, so every fixture asserts both forward encoding and reversibility. The covered edge flags protect storage systems that reject or mishandle names with leading or trailing spaces, periods, tildes, CR, LF, horizontal tab, or vertical tab. The normal flags in the same rows verify that edge processing composes with ordinary reserved-character substitution and quoting.

## Important APIs, Types, And Data

The fixture uses the `testCase` type from `encoder_test.go`:

```go
type testCase struct {
	mask MultiEncoder
	in   string
	out  string
}
```

The data targets `MultiEncoder` from `encoder.go`, especially these APIs:

- `func (mask MultiEncoder) Encode(in string) string`
- `func (mask MultiEncoder) Decode(in string) string`
- `func (mask MultiEncoder) Has(flag MultiEncoder) bool`

The edge flags exercised in this chunk are:

- `EncodeLeftSpace`: leading ASCII space becomes `␠`, and leading literal `␠` is quoted as `‛␠`.
- `EncodeRightSpace`: trailing ASCII space becomes `␠`, and trailing literal `␠` is quoted as `‛␠`.
- `EncodeLeftPeriod`: leading `.` becomes `．`, and leading literal `．` is quoted as `‛．`.
- `EncodeRightPeriod`: trailing `.` becomes `．`, and trailing literal `．` is quoted as `‛．`.
- `EncodeLeftTilde`: leading `~` becomes `～`, and leading literal `～` is quoted as `‛～`.
- `EncodeLeftCrLfHtVt`: leading tab, newline, vertical tab, or carriage return becomes its Unicode control-picture form, with pre-existing control pictures quoted.
- `EncodeRightCrLfHtVt`: the equivalent transformation for trailing tab, newline, vertical tab, or carriage return.

The ordinary flags combined with those edge flags include `EncodeZero`, `EncodeSlash`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, `EncodeCrLf`, `EncodeDel`, and `EncodeCtl`.

Within this exact range, the most common edge dimensions are right-space cases, CR/LF/HT/VT edge cases, and right-period cases. A quick count of visible masks gives 896 rows containing `EncodeRightSpace`, 308 containing `EncodeLeftCrLfHtVt`, 308 containing `EncodeRightCrLfHtVt`, 250 containing `EncodeRightPeriod`, 160 containing `EncodeLeftSpace`, 160 containing `EncodeLeftPeriod`, and 90 containing `EncodeLeftTilde`. The first ordinary mask token is spread across all normal character classes, with most appearing 56 to 60 times in this slice and `EncodeDel` appearing 72 times because it participates in both printable/control-picture edge combinations here.

## Control Flow

This source range has no runtime branches of its own. The relevant test control flow is in `TestEncodeSingleMaskEdge`:

1. Iterate over `testCasesSingleEdge`.
2. For each `tc`, assign `e := tc.mask`.
3. Call `got := e.Encode(tc.in)` and compare it with `tc.out`.
4. Call `got2 := e.Decode(got)` and compare it with `tc.in`.

The implementation control flow that these rows stress is in `MultiEncoder.Encode`:

1. Return unchanged for `EncodeRaw` and empty input.
2. Handle special dot-only names if `EncodeDot` is set.
3. Compute at most one prefix replacement in priority order: left space, left period, left tilde, then left CR/LF/HT/VT.
4. Compute at most one suffix replacement in priority order: right space, right period, then right CR/LF/HT/VT.
5. Encode the remaining middle substring for ordinary reserved characters and control classes.
6. Reassemble `prefix + encodedMiddle + suffix`.

The matching `MultiEncoder.Decode` reverses the same shape: it first detects a quoted or unquoted edge prefix, then a quoted or unquoted edge suffix, then decodes the remaining middle substring. The generated cases intentionally include raw edge characters and their already-encoded Unicode substitutes to verify that quoting disambiguates literal encoded-looking names from names produced by `Encode`.

## State And Persistence Behavior

The chunk is static generated test data persisted in the source tree. It does not hold runtime state, create files, mutate configuration, or persist encoder results. Its only state-like behavior is as a regression oracle: when `go test` compiles the `encoder` package, these literals become an in-memory slice used by the table-driven tests.

The generator is the persistence owner. `encoder_cases_test.go` is regenerated by `go generate` through `go run ./internal/gen/main.go`; manual edits would be overwritten and can desynchronize the checked-in table from the generator's intended matrix.

## Dependencies And Integration Points

Primary dependencies and integration points are:

- `sources/user-network-fs/rclone/lib/encoder/encoder.go`: defines `MultiEncoder`, the bit flags, `QuoteRune`, `Encode`, and `Decode`.
- `sources/user-network-fs/rclone/lib/encoder/encoder_test.go`: defines `testCase` and the tests that consume `testCasesSingleEdge`.
- `sources/user-network-fs/rclone/lib/encoder/internal/gen/main.go`: generates this table. Its `buildEdgeTestString` logic places edge characters at the first, second, penultimate, and final positions and emits both raw and pre-encoded variants.
- Backend encoding presets such as OS-specific encoder masks indirectly depend on this behavior because rclone remotes choose combinations of `MultiEncoder` flags to represent filesystem restrictions.
- The Go compiler and UTF-8 string handling are part of the test surface because many fixtures mix ASCII bytes, Unicode fullwidth characters, Unicode control pictures, and the quote rune.

The chunk also validates the interaction between edge-only rules and normal middle-string rules. For example, rows combining `EncodeSlash` with edge flags assert that `/` and `／` are transformed or quoted in the middle while only boundary spaces/periods/control characters are treated as edge cases. Rows combining `EncodeCtl`, `EncodeCrLf`, or `EncodeDel` with edge flags check overlap between general control-character encoding and boundary-specific control handling.

## Risks And Maintenance Notes

- The table is generated and very large. Hand editing a row is risky because the generator can later rewrite it, and a single changed literal can break the encode/decode round-trip invariant.
- Edge priority is significant. `Encode` only emits one prefix and one suffix; when multiple left or right edge flags match the same boundary position, the earlier checks win. These fixtures capture that priority and should change only with an intentional compatibility decision.
- Quoting behavior is subtle. Literal Unicode substitutes such as `␠`, `．`, `～`, control pictures, and fullwidth punctuation must be quoted when they appear where the encoder would otherwise produce them. Missing quote coverage can cause irreversible decode collisions.
- The chunk includes strings with control bytes, DEL, Unicode fullwidth punctuation, Greek letters, and encoded-looking glyphs. Tooling that normalizes Unicode, trims whitespace, interprets escapes, or rewrites generated files can silently corrupt test meaning.
- `EncodeCrLf` and `EncodeCtl` overlap with `EncodeLeftCrLfHtVt` and `EncodeRightCrLfHtVt`. Boundary characters should be handled as prefix/suffix first, while middle characters should follow ordinary class encoding; regressions here can affect remotes that restrict control characters differently at boundaries.
- Because this is only a slice of `testCasesSingleEdge`, it is not independently meaningful as a complete generated matrix. Merge or reconciliation tooling should treat it as one contiguous chunk of the source file, not as a standalone test specification.

## Test Signals

The direct signal is `TestEncodeSingleMaskEdge` in the `encoder` package. For every row in this chunk, a passing test means:

- `mask.Encode(in)` exactly equals the generated `out`.
- `mask.Decode(out)` exactly reconstructs `in`.
- Prefix and suffix transformations compose with the ordinary character-class transformation in the same mask.
- Pre-existing encoded-looking Unicode characters at active edge positions are preserved by quote insertion and decode correctly.

Useful invariants from this chunk:

- 1,086 `testCase` entries are visible in the requested range.
- Case comments run from `// 3317` through `// 4402`.
- All entries belong to `testCasesSingleEdge`; none define new functions, types, or package state.
- Rows are intentionally dense around right-space, CR/LF/HT/VT boundary handling, and right-period handling.
- Generated outputs use `QuoteRune` (`‛`) to disambiguate literal encoded forms from encoder-produced forms.

Relevant smoke command for this file-level behavior is:

```sh
go test ./lib/encoder -run 'TestEncodeSingleMaskEdge|TestEncodeSingleMask|TestEncodeDoubleMaskEdge'
```

Run that from the rclone source root under `sources/user-network-fs/rclone` when validating changes to `encoder.go`, `encoder_test.go`, or `lib/encoder/internal/gen/main.go`.

### subset-b-009789: lines 36349-40678

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 36349-40678

## Purpose

This chunk is a generated segment of `testCasesDoubleEdge`, the table consumed by `TestEncodeDoubleMaskEdge` in `lib/encoder/encoder_test.go`. It validates `MultiEncoder` behavior when one ordinary character-class mask is combined with two edge-only masks. The cases in this range cover the end of the `EncodeRightPeriod | EncodeLeftTilde` combinations and then move into `EncodeRightPeriod | EncodeLeftCrLfHtVt` and `EncodeRightCrLfHtVt | EncodeLeftCrLfHtVt`.

The table is generated by `lib/encoder/internal/gen/main.go` and is explicitly marked `DO NOT EDIT`. Each entry has a `mask`, raw input `in`, and expected encoded output `out`; the test harness also decodes `out` and expects the original `in`, so the table asserts both forward substitution and reversibility.

## Important APIs, Types, and Functions

- `testCase` is defined in `encoder_test.go` with `mask MultiEncoder`, `in string`, and `out string`.
- `testCasesDoubleEdge` starts earlier in this generated file and is a `[]testCase` fixture table. This chunk contains cases numbered approximately `4403` through `5487`.
- `TestEncodeDoubleMaskEdge` iterates this table, calls `tc.mask.Encode(tc.in)`, compares it with `tc.out`, then calls `tc.mask.Decode(got)` and expects `tc.in`.
- `MultiEncoder.Encode` is the implementation under test. For this chunk, the relevant logic is:
  - leading edge handling for `EncodeLeftTilde` and `EncodeLeftCrLfHtVt`;
  - trailing edge handling for `EncodeRightPeriod` and `EncodeRightCrLfHtVt`;
  - body substitutions for masks such as `EncodeSlash`, `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, and related fullwidth/quoted forms.
- `QuoteRune` is `‛`. It is inserted before already-encoded reserved runes, symbol control runes, or edge replacement runes when needed to preserve round-trip identity.
- `internal/gen/main.go` generates these cases via `allEdges`, `allMappings`, `buildEdgeTestString`, and `fixEdges`.

## Control Flow Covered

The range is part of the generated nested loop over two distinct edges and one ordinary mapping mask:

1. Build a 30-rune randomized input/output baseline that includes printable ASCII, fullwidth printable runes, encodable characters, encoded characters, and Greek filler.
2. Seed both edge positions with the first edge's original/replacement rune and inject each second-edge original rune into near-edge positions.
3. Call generator-side `fixEdges`, which mirrors `MultiEncoder.Encode` edge behavior:
   - if the leftmost rune matches a left-edge original rune, replace it with the left-edge encoded rune;
   - if the leftmost rune is already the encoded left-edge rune, prefix `QuoteRune`;
   - if the rightmost rune matches a right-edge original rune, replace it with the right-edge encoded rune;
   - if the rightmost rune is already the encoded right-edge rune, prefix `QuoteRune`.
4. Emit the table row with a combined mask such as `EncodeLtGt | EncodeRightPeriod | EncodeLeftTilde`.
5. Runtime tests compare `Encode` output and verify `Decode` reverses it.

Within the source range, common control-flow patterns are visible:

- For `EncodeRightPeriod | EncodeLeftTilde`, a trailing `.` becomes `．`, and a trailing existing `．` becomes `‛．`; a leading `~` becomes `～`, and a leading existing `～` becomes `‛～`. The chunk begins after the leading tilde examples for `EncodeSingleQuote`, then continues through many body mask combinations.
- For `EncodeRightPeriod | EncodeLeftCrLfHtVt`, a leading tab/newline/vertical-tab/carriage-return becomes the corresponding symbol rune (`␉`, `␊`, `␋`, `␍`), a leading already-symbolized rune is quoted, and a trailing `.` is still handled independently.
- For `EncodeRightCrLfHtVt | EncodeLeftCrLfHtVt`, both first and last characters can be CR/LF/HT/VT edge candidates. The table checks raw and already-encoded forms at both ends, including quoted suffix symbols such as `‛␉`.

## State and Persistence Behavior

There is no runtime state mutation or persistence in this file. The generated table is static Go source compiled into the test binary. The only stateful behavior relevant to this chunk is test-local iteration over table entries and the temporary strings built by `Encode` and `Decode`.

The generator uses a deterministic pseudo-random source with a default seed, so the fixture content is stable once generated. Regeneration can reorder or rewrite the table if generator logic, seed, mappings, or edge definitions change.

## Dependencies and Integration Points

- Depends on `lib/encoder/encoder.go` constants and methods, especially `MultiEncoder`, `Encode*` bit flags, `QuoteRune`, `Encode`, and `Decode`.
- Depends on `encoder_test.go` for the `testCase` type and table-driven test harness.
- Generated by `lib/encoder/internal/gen/main.go`, which imports `github.com/rclone/rclone/lib/encoder` and mirrors its mapping rules.
- Integrated into Go tests for the `encoder` package. The source file is package-local test data rather than production code.
- The encoded substitutions align with rclone's broader filename/path encoding contracts, where restrictive remotes can choose a `MultiEncoder` mask and rely on reversible filename translation.

## Risks and Edge Cases

- Edge precedence is important. `MultiEncoder.Encode` handles prefixes first and suffixes second, then body substitutions. These cases ensure the same rune class is treated differently at edge positions than in the middle of the string.
- Quoting already-encoded edge runes is a major round-trip risk. Without `‛` before existing `．`, `～`, `␉`, `␊`, `␋`, or `␍` at active edges, `Decode` would collapse distinct original names.
- `EncodeLeftCrLfHtVt` and `EncodeRightCrLfHtVt` overlap semantically with `EncodeCtl` and `EncodeCrLf`. The generator intentionally filters invalid masks where those combinations would conflict, so absent combinations in this region are intentional.
- The generated expectations must stay in sync with `encoder.go`. Because generator logic duplicates encoding semantics, a bug replicated in both implementation and generator could weaken the tests if fixtures are regenerated after the bug is introduced.
- Unicode fullwidth and control-symbol runes are mixed with raw control bytes and escape sequences. Manual edits are high risk, especially around `\t`, `\n`, `\v`, `\r`, NUL, DEL, and pre-encoded symbol runes.
- This chunk is not exhaustive by itself. Its value comes from coverage across the larger generated table and the round-trip check in the harness.

## Test Signals

- Primary signal: `go test ./lib/encoder` from the rclone source tree should run `TestEncodeDoubleMaskEdge` and fail on the first mismatched fixture or non-reversible decode.
- A failure in this chunk would indicate a regression in combined edge handling, body reserved-character mapping, or quoting of already-encoded runes.
- Case numbering in failure subtests maps directly to comments in `testCasesDoubleEdge`, making entries in this chunk locatable by their generated numeric comments.
- Strong examples in this range include:
  - right-period behavior: trailing `.` to `．` and trailing `．` to `‛．`;
  - left-tilde behavior: leading `~` to `～` and leading `～` to `‛～`;
  - left CR/LF/HT/VT behavior: leading `\t`, `\n`, `\v`, `\r` to `␉`, `␊`, `␋`, `␍`;
  - right CR/LF/HT/VT behavior: trailing raw tab/newline/vertical-tab/carriage-return to the matching symbol and trailing existing symbols to quoted symbols.

### subset-b-009790: lines 40679-41845

# sources/user-network-fs/rclone/lib/encoder/encoder_cases_test.go lines 40679-41845

## Scope

This chunk covers the final slice of the generated encoder case table in `lib/encoder/encoder_cases_test.go`. The requested range starts inside the tail of test case `5484`, then includes complete cases `5485` through `5775`, and ends with the closing brace of `testCasesDoubleEdge`.

The file is generated by `lib/encoder/internal/gen/main.go` and is not hand-authored application logic. Its records are Go composite literals of the local `testCase` type:

- `mask MultiEncoder`
- `in string`
- `out string`

These cases are consumed by `TestEncodeDoubleMaskEdge` in `lib/encoder/encoder_test.go`, which verifies both `MultiEncoder.Encode(tc.in) == tc.out` and `MultiEncoder.Decode(tc.out) == tc.in` for every generated record.

## Purpose

This range provides regression coverage for interactions between suffix/prefix-only encoding flags and ordinary character-class encoding flags. The dominant edge under test is `EncodeRightCrLfHtVt`, which applies only to trailing horizontal tab, line feed, vertical tab, or carriage return. The chunk checks that trailing CR/LF/HT/VT handling composes correctly with:

- `EncodeLeftCrLfHtVt`, for names that also have leading CR/LF/HT/VT edge characters.
- `EncodeRightSpace`, for names where trailing space and trailing CR/LF/HT/VT are both potentially relevant suffix-only encodings.
- `EncodeRightPeriod`, for names where trailing period and trailing CR/LF/HT/VT are both potentially relevant suffix-only encodings.
- Regular per-rune encoders such as `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, and `EncodeDel`.

The cases preserve invertibility when a string already contains encoded-looking runes such as `␉`, `␊`, `␋`, `␍`, fullwidth punctuation, `␀`, or `␡`. Those already-encoded runes are quoted with `QuoteRune` (`‛`) when the active mask would otherwise treat them as encoded output.

## Important APIs, Types, And Functions

The source chunk itself declares no functions. It is data for encoder tests. The relevant APIs are:

- `type MultiEncoder uint` in `encoder.go`: bitmask type that combines `Encode*` flags.
- `type testCase` in `encoder_test.go`: table record with `mask`, `in`, and `out`.
- `func (mask MultiEncoder) Encode(string) string`: applies fullwidth/control-symbol substitutions and quote escaping.
- `func (mask MultiEncoder) Decode(string) string`: reverses encoded names back to raw names.
- `TestEncodeDoubleMaskEdge`: iterates `testCasesDoubleEdge`, runs subtests by generated numeric index, and checks encode plus decode round-trip.

The core flags represented in this chunk are:

- `EncodeRightCrLfHtVt`: trailing `\t`, `\n`, `\v`, and `\r` map to the corresponding Unicode control pictures `␉`, `␊`, `␋`, and `␍`; pre-existing trailing control pictures are quoted.
- `EncodeLeftCrLfHtVt`: the same mapping for the first rune/byte of the name.
- `EncodeRightSpace`: trailing ASCII space maps to `␠`; pre-existing trailing `␠` is quoted.
- `EncodeRightPeriod`: trailing `.` maps to `．`; pre-existing trailing `．` is quoted.
- Per-rune flags map restricted ASCII punctuation to fullwidth variants, and quote pre-existing fullwidth variants when needed.
- `EncodeZero` maps NUL to `␀` and quotes pre-existing `␀`.
- `EncodeDel` maps `0x7f` to `␡` and quotes pre-existing `␡`.

## Covered Case Families

The line range includes 291 complete records plus the visible tail of case `5484`. The complete records are grouped mechanically by mask:

- Tail of the `EncodeDollar | EncodeRightCrLfHtVt | EncodeLeftCrLfHtVt` family, then full families for `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, and `EncodeDel` combined with `EncodeRightCrLfHtVt | EncodeLeftCrLfHtVt`.
- Full four-case families for `EncodeZero`, `EncodeSlash`, `EncodeSingleQuote`, `EncodeBackQuote`, `EncodeLtGt`, `EncodeSquareBracket`, `EncodeSemicolon`, `EncodeExclamation`, `EncodeDollar`, `EncodeDoubleQuote`, `EncodeColon`, `EncodeQuestion`, `EncodeAsterisk`, `EncodePipe`, `EncodeHash`, `EncodePercent`, `EncodeBackSlash`, and `EncodeDel` combined with `EncodeRightCrLfHtVt | EncodeRightSpace`.
- Full four-case families for the same set combined with `EncodeRightCrLfHtVt | EncodeRightPeriod`.

The sixteen-case `EncodeRightCrLfHtVt | EncodeLeftCrLfHtVt` families exercise each CR/LF/HT/VT byte at both left and right edges. They verify:

- left-edge tab/newline/vertical-tab/carriage-return is encoded only at the start of the name;
- right-edge tab/newline/vertical-tab/carriage-return is encoded only at the end of the remaining name;
- a pre-existing leading or trailing control-picture rune is quoted;
- interior edge-like characters are not treated as edge characters unless another active encoder matches them.

The four-case `EncodeRightCrLfHtVt | EncodeRightSpace` and `EncodeRightCrLfHtVt | EncodeRightPeriod` families focus on suffix precedence. They show that the suffix-only handling in `Encode` checks `EncodeRightSpace`, then `EncodeRightPeriod`, then `EncodeRightCrLfHtVt`, and only one suffix transform is applied before the general per-rune pass.

## Control Flow

This generated table has no runtime control flow by itself. The effective test flow is:

1. `go test ./lib/encoder` compiles `encoder_cases_test.go` together with `encoder_test.go`.
2. `TestEncodeDoubleMaskEdge` loops over `testCasesDoubleEdge`.
3. For each record, it copies `tc.mask` to `e`.
4. It calls `e.Encode(tc.in)` and compares the result with the generated `tc.out`.
5. It calls `e.Decode(got)` and requires the decoded result to equal the original `tc.in`.

The `Encode` implementation path relevant to this chunk is:

1. Return immediately for `EncodeRaw` or empty strings; neither path is the focus here.
2. Apply special whole-name dot handling only if `EncodeDot` is set; not represented in this chunk.
3. Apply prefix-only edge handling. For this range, `EncodeLeftCrLfHtVt` may consume a leading `\t`, `\n`, `\v`, or `\r`, or quote a leading `␉`, `␊`, `␋`, or `␍`.
4. Apply suffix-only edge handling. For this range, `EncodeRightSpace`, `EncodeRightPeriod`, or `EncodeRightCrLfHtVt` may consume the trailing edge character or quote an already-encoded trailing rune.
5. If no prefix/suffix was generated, `Encode` uses `strings.IndexFunc` to find the first rune that might need replacement.
6. It streams the remaining body through a `bytes.Buffer`, mapping NUL/control/fullwidth/punctuation runes according to the active mask and quoting ambiguous encoded forms.
7. It appends any generated suffix after the body.

The generated expected strings in this chunk encode those steps. For example, cases with input ending in `\t` expect a final `␉`; cases ending in `␉` expect `‛␉`; cases with active punctuation masks also transform the selected punctuation character in the body.

## State And Persistence Behavior

The table is static generated Go test data. It does not persist state, open files, or touch external systems at runtime. Its persistence behavior is source-control oriented:

- `encoder_cases_test.go` is regenerated by `go generate` using `lib/encoder/internal/gen/main.go`.
- The generator uses a deterministic seed by default, so the large table should be reproducible when generator logic and inputs are unchanged.
- The table persists exact examples of edge-case names, including control bytes, Unicode control pictures, fullwidth punctuation, and quote-rune collisions.

Runtime state is limited to temporary strings and buffers inside `MultiEncoder.Encode` and `Decode`, plus Go test subtest bookkeeping.

## Dependencies And Integration Points

Local dependencies and integration points:

- `lib/encoder/encoder.go`: owns `MultiEncoder`, `QuoteRune`, the `Encode*` constants, and encode/decode algorithms validated by these cases.
- `lib/encoder/encoder_test.go`: owns `testCase` and the generated-table test loops.
- `lib/encoder/internal/gen/main.go`: emits `testCasesSingle`, `testCasesSingleEdge`, and `testCasesDoubleEdge`.
- Rclone backend packages consume encoder masks indirectly through filesystem encoding configuration; regressions here can affect remote path/name round-tripping across restrictive storage systems.

Standard-library dependencies involved in the tested implementation include `bytes.Buffer`, `strings.IndexFunc`, and `unicode/utf8` for safe rune scanning and byte-preserving invalid UTF-8 handling. This chunk does not directly exercise invalid UTF-8 flags, but it does rely on UTF-8-aware first/last-rune handling for quoted Unicode control-picture and fullwidth suffixes.

## Risks And Maintenance Notes

- The requested range starts mid-record at the `out` field of case `5484`, so this chunk alone is not syntactically complete Go. It must be interpreted within the full generated file.
- The range ends at the end of `testCasesDoubleEdge`; changes to generator ordering can shift line assignments and chunk boundaries even when behavior is equivalent.
- Suffix precedence is subtle. `EncodeRightSpace`, `EncodeRightPeriod`, and `EncodeRightCrLfHtVt` are mutually exclusive in a single pass because `suffix == ""` gates later suffix transforms. A change in that order would invalidate many expected outputs here.
- Prefix/suffix transforms remove only one edge character before the body pass. Names with multiple edge-like characters rely on the remaining character either staying literal or being processed by general per-rune logic; this is a common source of off-by-one and double-encoding regressions.
- Quoting already-encoded forms is essential for lossless decode. Any change to `QuoteRune` handling, control-picture ranges, or fullwidth punctuation mapping can break round-trip guarantees.
- The generated strings include escaped control bytes and many visually similar Unicode characters. Manual edits are risky and should be avoided; regenerate instead.

## Test Signals

Primary test signal:

- `go test ./lib/encoder` should run `TestEncodeDoubleMaskEdge` and pass every case in this range.

Useful focused checks when changing encoder behavior:

- run subtests around generated indexes `5485` through `5775` if using `go test -run` with subtest filtering;
- verify `EncodeRightCrLfHtVt | EncodeLeftCrLfHtVt` cases still encode only the first and last CR/LF/HT/VT bytes and quote pre-existing edge control-picture runes;
- verify combinations with `EncodeRightSpace` and `EncodeRightPeriod` preserve the documented suffix precedence;
- verify `Decode(Encode(name)) == name` for strings containing both raw restricted characters and already-encoded-looking fullwidth/control-picture runes;
- regenerate `encoder_cases_test.go` after generator changes and review broad table churn rather than editing this file manually.
