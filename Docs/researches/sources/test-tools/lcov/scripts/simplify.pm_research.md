# sources/test-tools/lcov/scripts/simplify.pm

Purpose: genhtml `--simplify-script` callback that rewrites displayed function names using ordered substitution regexps. It affects function detail presentation only, not stored coverage identities.

Important APIs: package `simplify` exports `new`. Options are mutually exclusive `--file regexp_file_name` or repeated `--re regexp`, with optional `--separator`. Methods are `simplify($name)`, `start`, `save`, `restore`, and `finalize`.

Control flow and state: constructor loads regexps from a file or command line, validates patterns through `lcovutil::verify_regexp_patterns`, expects substitution form `s<sep>pattern<sep>replacement<sep>g`, precompiles pattern components, and stores a per-pattern match count. `simplify` applies every substitution in order and increments the pattern count when it changes the name. `start/save/restore/finalize` support parallel callback aggregation and unused-pattern warnings.

Dependencies and integration: depends on `lcovutil` for regex validation and `warn_pattern_list`. Invoked by genhtml while rendering function tables.

Risks and test signals: the parser only accepts global substitutions with exactly three split fields, so escaped separators or flags other than `g` are unsupported. Replacement strings are used literally in Perl substitution context. Tests should verify file and inline patterns, separator handling, invalid patterns, parallel save/restore, and warning output for unused rules.
