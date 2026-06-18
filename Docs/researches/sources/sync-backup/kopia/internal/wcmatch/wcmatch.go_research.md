<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/wcmatch.go -->
# sources/sync-backup/kopia/internal/wcmatch/wcmatch.go

- Purpose: Implements .gitignore-style wildcard matcher parsing and path matching.
- Important APIs/types/functions: `WildcardMatcher`, `Options`, `Option`, `IgnoreCase`, `BaseDir`, `Pattern`, `Negated`, `Options`, `NewWildcardMatcher`, `Match`, `doMatch`, `indexOf`.
- Control flow: Parser trims unescaped whitespace, handles negation/rooting/base directory, implicit `**/`, directory-only suffixes, escapes, stars, sequences, ranges, and POSIX-like character classes. Matching recursively consumes tokens and path runes with abort states for `*`/`**` backtracking.
- State and persistence: Matchers store original pattern, parsed tokens, options, and flags only.
- Dependencies and integration points: Used by path filtering/exclusion behavior; depends on `unicode`, `strings`, and `pkg/errors`.
- Risks and edge cases: Recursive matching can be expensive for adversarial patterns; escape/class/rooting rules are subtle.
- Test signals: `wcmatch_test.go` has broad table coverage for base dirs, case sensitivity, recursion, directories, negation, whitespace, errors, and character classes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/wcmatch.go -->
