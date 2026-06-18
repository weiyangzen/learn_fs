# sources/sync-backup/borg/src/borg/testsuite/helpers/shellpattern_test.py

Purpose: verifies Borg's shell-pattern-to-regex translator for literals, separators, glob stars, double-stars, character sets, inverted sets, groups, Unicode, and custom match endings.

Important APIs and control flow: helper `check` compiles `shellpattern.translate(pattern)` and matches paths. Large parametrized match/mismatch tables cover `?`, `*`, `**` across path separators, nested directory matching, sets including `]`, inverted sets, brace groups including nested groups and empty alternatives, non-ASCII characters, and escaping-like literal behavior. `test_match_end` verifies default end-of-string matching and a custom optional suffix regex.

State and persistence: pure regex compilation/matching; no persistent state.

Dependencies and integration points: depends on `helpers.shellpattern.translate`, Python `re`, and pytest. This translator backs include/exclude pattern semantics.

Risks: separator handling is subtle: single-star and question mark must not cross separators, while `**/` has directory-layer semantics. Brace parsing can be ambiguous with malformed groups.

Test signals: every pattern in match tables must match and every mismatch case must not, plus exact custom suffix behavior.
