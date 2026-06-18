# sources/sync-backup/borg/src/borg/helpers/shellpattern.py

## Purpose
Translates Borg shell-style path patterns, including directory wildcards and brace alternatives, into regular expressions.

## Important APIs, Types, And Functions
`translate(pat, match_end=r"\Z")` is the public converter. `_parse_braces` identifies matching unescaped brace pairs. `_translate_alternatives` rewrites shell brace alternatives into regex groups.

## Control Flow
Brace alternatives are translated first, converting unescaped commas inside matched brace pairs to `|` and only changing braces to parentheses when alternatives exist. `translate` then scans the pattern: `**/` matches zero or more directory levels, `*` and `?` do not cross the platform separator, bracket classes are preserved with negation handling, unescaped regex group characters from alternatives are allowed, and everything else is escaped.

## State And Persistence
No persistent state. Uses local scan state and a `LifoQueue` for brace matching.

## Dependencies And Integration Points
Used by Borg pattern matching and archive filtering. Depends on `os.path.sep` and `re`. Results are consumed as regex strings with `(?ms)` flags and caller-provided ending behavior.

## Risks And Edge Cases
Nested and adjacent brace groups are subtle. Escaped braces, commas, and pipes must remain literal. `**/` behavior depends on the platform path separator, while Borg archive paths often use `/`; callers must normalize consistently. Bracket parsing must avoid invalid regex for unterminated classes.

## Test Signals
Existing shellpattern tests should cover `*`, `?`, bracket classes, `**/`, custom `match_end`, escaped metacharacters, adjacent/nested brace alternatives, alternatives without commas, and platform separator assumptions.
