# sources/test-tools/lcov/scripts/select.pm

Purpose: genhtml `--select-script` callback that decides whether a line or coverpoint is interesting enough to include, based on differential TLA category, commit/changelist, owner regexp, or age range.

Important APIs: package `select` exports `new`. Options are `--range`, `--owner`, `--tla`, `--sha`/`--cl`, and `--separator`. Runtime methods are `select($lineData, $annotateData, $filename, $lineNo)`, `save`, `restore`, and `finalize`.

Control flow and state: constructor splits list arguments, validates regexps and TLA names against `%lcovutil::tlaColor`, validates numeric ranges, and checks that annotation/diff/baseline prerequisites exist for selected criteria. The object stores criteria arrays, match counters, plaintext labels, and total seen coverpoints. `select` first matches coverage TLA, then annotation age, commit prefix regex, and owner full-name regex; any match returns true and increments criterion counters. `finalize` reports match counts.

Dependencies and integration: depends on `lcovutil`, `SourceFile::annotateScript`, `@main::base_filenames`, and `$main::diff_filename` provided by genhtml. Annotation data must provide `age`, `commit`, and `full_name`; line data must provide `tla`, `type`.

Risks and test signals: age matching uses equality against provided range objects rather than checking min/max bounds, which is suspicious. Regexps are user supplied. Tests should cover TLA-only, owner/SHA with annotation enabled, prerequisite warnings, save/restore aggregation, and final count output.
