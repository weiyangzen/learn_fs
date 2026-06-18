# sources/sync-backup/bup/test/int/test_options.py

Purpose: covers bup's custom option parser, option dictionary aliases, negated options, defaults parsed from optspec text, short option clustering, long options, and numeric compression aliases.

Important APIs/types/functions: `options.OptDict`, `options.Options`, invalid optspec fixtures, and the multiline `optspec` containing aliases such as `q,quiet`, `s,smart,no-stupid`, `#,compress=`, and default annotations.

Control flow: `test_optdict()` builds an alias map, writes values through canonical and negated keys, and checks attribute access. `test_invalid_optspec()` ensures empty/minimal/malformed optspecs do not crash parsing. `test_options()` parses two argument vectors and validates flag history, extra arguments, occurrence counts, typed parameter conversion, long-only toggles, negated aliases, default values, and `#` compression option mapping.

State and persistence behavior: pure parser tests with no external state.

Dependencies/integration points: targets the parser used by bup command-line tools. The flags list is an integration contract for callers that need both parsed state and original flag order.

Risks and test signals: optspec text parsing is brittle because behavior is inferred from whitespace and bracketed defaults. Exact assertions detect regressions in alias normalization, negation semantics, numeric conversion, and leftover argument handling.
