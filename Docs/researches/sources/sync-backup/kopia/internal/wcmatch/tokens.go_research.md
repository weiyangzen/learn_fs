<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/tokens.go -->
# sources/sync-backup/kopia/internal/wcmatch/tokens.go

- Purpose: Defines token types used by wildcard parser and matcher.
- Important APIs/types/functions: `token`, `tokenAnyChar`, `tokenDirSep`, `tokenStar`, `tokenRune`, `tokenSeq`, `seqToken`, `seqTokenRuneRange`, `seqTokenRune`, `seqTokenClass`, `isStar`, `isDirSep`.
- Control flow: Token structs implement `String` and sequence tokens implement `match`; utility functions classify tokens during recursive matching.
- State and persistence: Token values are immutable in-memory parse results.
- Dependencies and integration points: Used by `wcmatch.go`; depends on `fmt` and `strings`.
- Risks and edge cases: String forms are useful for debugging but not a complete re-serialization guarantee.
- Test signals: Indirectly covered by wildcard parser/matcher tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/tokens.go -->
