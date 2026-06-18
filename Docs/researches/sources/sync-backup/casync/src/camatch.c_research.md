# sources/sync-backup/casync/src/camatch.c

## Purpose
`camatch.c` implements the mutable and normalized representation of casync path match rules. It parses gitignore-like positive and negative glob patterns into a `CaMatch` tree, propagates unanchored rules into child directory subtrees, normalizes duplicate branches, and answers one-component match queries during archive tree traversal.

## Important APIs, Types, and Functions
The implementation revolves around `CaMatch` from `camatch.h`. `ca_match_new_from_file()` reads a pattern file via `openat()` and `read_line()`, ignoring blank lines and comments. `ca_match_new_from_strings()` builds the same structure from a string vector. `parse_line()` splits one rule into path components, rejects empty, `.` and `..` components, detects negation with `!`, marks patterns as anchored when they contain `/`, and sets `directory_only` when a component is followed by a slash. `ca_match_add_child()`, `ca_match_merge()`, `ca_match_make_writable()`, and `ca_match_normalize()` implement reference-counted tree mutation, copy-on-write, sorting, and duplicate subtree merging. `ca_match_test()` is the runtime matcher, returning positive match, negative match, no match, and optionally a subtree for recursion.

## Control Flow
Construction starts with `ca_match_alloc_subtree()`, creating an anchored directory-only inner root. Each input line is parsed into a chain of `CA_MATCH_INNER` nodes for intermediate directories and a `CA_MATCH_POSITIVE` or `CA_MATCH_NEGATIVE` leaf for the final component. Normalization recursively sorts children by type, name, anchoring, directory-only flag, and children, then attempts adjacent merges. Matching iterates direct children, carries unanchored directory rules forward into a returned subtree, applies `fnmatch(..., FNM_PERIOD)`, and gathers second-level children for matching directories. Negative matches override positives at the current level through the final `has_negative ? false : has_positive` decision.

## State and Persistence
State is entirely in-memory and reference-counted. The object is immutable by convention once shared; write operations reject shared nodes or copy before modification. File persistence is limited to reading match rules from a caller-supplied directory file descriptor and filename. No normalized representation is written back to disk.

## Dependencies and Integration Points
This file depends on `util.h` helpers for allocation, string vectors, cleanup attributes, line reading, and string predicates. It uses libc `fnmatch()` for glob evaluation. `caencoder.c` includes `camatch.h`, so these rules are integrated into archive encoding and filesystem traversal decisions.

## Risks
The parser accepts only a strict path-component grammar; escaped `!`, whitespace-sensitive patterns, and full gitignore semantics are not implemented. `fnmatch()` errors other than no-match become `-EINVAL`, so malformed patterns can surface late. Normalization is best-effort: failures can leave an equivalent but not fully normalized tree. The return value from `ca_match_test()` is easy to misuse because `0` means either no positive match or a negative match unless the caller tracks policy.

## Test Signals
`test/test-camatch.c` exercises string parsing, node attributes, normalization, subtree propagation, positive and negative matches, anchored paths, directory-only rules, and equality checks. Additional useful tests would cover invalid input lines, file-based parsing, repeated normalization after merge failures, and patterns with leading/trailing duplicate slashes.
