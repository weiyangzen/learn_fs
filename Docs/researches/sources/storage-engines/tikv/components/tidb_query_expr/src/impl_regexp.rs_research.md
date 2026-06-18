# sources/storage-engines/tikv/components/tidb_query_expr/src/impl_regexp.rs

## Purpose
`impl_regexp.rs` implements TiDB regular expression scalar functions for UTF-8 strings: `REGEXP`/`REGEXP_LIKE`, `REGEXP_SUBSTR`, `REGEXP_INSTR`, and `REGEXP_REPLACE`. It handles MySQL match-type flags, collation-driven default case sensitivity, constant-expression precompilation, character-position semantics, and capture substitution in replacements.

## Important APIs, Types, and Functions
Constants such as `PATTERN_IDX`, `LIKE_MATCH_IDX`, `SUBSTR_MATCH_IDX`, `INSTR_MATCH_IDX`, and `REPLACE_MATCH_IDX` describe argument positions for raw variadic RPN functions. `invalid_pos_error`, `is_valid_match_type`, `get_match_type`, `build_regexp`, `build_regexp_from_args`, and `init_regexp_data` are the shared regex construction path.

The public RPN functions are `regexp_like<C: Collator>`, `regexp_substr<C: Collator>`, `regexp_instr<C: Collator>`, and `regexp_replace<C: Collator>`. They are generic over the TiDB collation implementation so case-insensitive collations can inject the `i` flag by default.

Replacement support is modeled by `ReplaceInstruction`, with `SubstitutionNum(usize)` and `Literal(Vec<u8>)`. `ReplaceMetaData` stores an optional precompiled `Regex` and optional parsed replacement instructions. `init_regexp_replace_data` precomputes both when the expression tree has constant pattern and replacement children. `init_replace_instructions` parses backslash escapes and one-digit capture substitutions.

## Control Flow
During expression build, metadata mappers inspect `tipb::Expr` children. If the pattern and optional match type are constant bytes/string expressions, `init_regexp_data` compiles a `regex::Regex` once and stores it in function metadata. If not, evaluation calls `build_regexp_from_args` per row. `regexp_replace` similarly pre-parses constant replacement expressions into instructions.

`get_match_type` starts with `i` when the collation is case-insensitive, accepts only `i`, `c`, `m`, and `s`, and applies flags left-to-right with `c` removing `i`. `build_regexp` rejects empty patterns, converts bytes to UTF-8, prepends inline Rust regex flags such as `(?ims)`, and maps regex compilation failures to `Error::regexp_error`.

`regexp_like` converts the expression bytes to UTF-8 and returns whether the regex matches. `regexp_substr` optionally trims the input by 1-based character position, normalizes occurrence values below 1 to 1, and returns the selected match as bytes. `regexp_instr` follows the same position and occurrence logic, validates return option 0 or 1, and returns a 1-based character offset for match start or end, or 0 if not found.

`regexp_replace` optionally preserves the prefix before the 1-based character position, treats occurrence 0 as replace all and negative occurrence as 1, then iterates captures. For every match it appends the unmatched slice and then executes replacement instructions. `\0` references the full match and `\1` through `\9` reference capture groups; missing capture numbers are regexp errors. A trailing backslash in the replacement is ignored by the parser.

## State and Persistence Behavior
There is no durable state. The only retained state is expression metadata containing compiled regexes and parsed replacement instructions. That metadata is tied to the built RPN expression and avoids repeated compilation for constant patterns or replacements. Dynamic patterns and match types allocate and compile during evaluation.

## Dependencies and Integration Points
The module depends on the Rust `regex` crate, `HashSet`, `Cow`, TiDB `Collator` and datatype traits, `tipb::Expr`/`ExprType`, and `tidb_query_codegen::rpn_fn` support for raw variadic functions and metadata mappers. `lib.rs` maps `RegexpSig`, `RegexpUtf8Sig`, and `RegexpLikeSig` through `map_regexp_like_sig`, and maps substring, instr, and replace signatures through their respective mapper functions.

## Risks and Edge Cases
Regex behavior is compatibility-sensitive. TiDB's documented support here is UTF-8 only, so invalid input or pattern bytes become UTF-8 errors. Empty patterns are explicitly rejected. The Rust `regex` crate is not MySQL ICU regex, so flags and unsupported constructs must be checked against TiDB compatibility expectations.

Position arguments are character indexes, not byte indexes. The code uses `char_indices().nth(pos - 1)` and later slices by byte offsets, so it handles multi-byte UTF-8 correctly as long as the input was valid UTF-8. `pos == 1` on an empty string is valid, while other out-of-range or non-positive positions are errors.

Replacement parsing supports only one digit after a backslash as a substitution number. Sequences such as `\12` mean capture 1 followed by literal `2`, matching the tests. Missing capture groups raise an error during replacement, not during metadata initialization. `get_match_type` stores flags in a `HashSet`, so flag ordering in the inline regex prefix is not stable, but for the supported flags order should not change semantics.

## Test Signals
Tests build full RPN expressions through `ExprDefBuilder` and `RpnExpressionBuilder`, not just direct function calls. They cover regexp like matches, invalid patterns, empty patterns, case flags, multiline and dot-matches-newline flags, rightmost `i`/`c` behavior, invalid match types, null propagation, substring and instr character positions over ASCII and multi-byte UTF-8, occurrence and return-option behavior, replacement from constants and column refs, replace-all versus specific occurrence, capture references including `\0`, out-of-range capture errors, trailing backslash handling, and long real-world URL-like strings.
