# sources/test-tools/lcov/scripts/threshold.pm

Purpose: criteria callback that enforces minimum coverage percentages for selected coverage types at any callback level, typically top or file.

Important APIs: package `threshold` exports `new`. Options include `--signoff`, `--line`, `--branch`, `--mcdc`, and `--function`. `check_criteria($name, $type, $db)` returns `(status, messages)`.

Control flow and state: constructor builds a hash of configured thresholds, requires at least one, and validates every value as numeric in `(0,100]`. `check_criteria` iterates configured keys present in the JSON DB, skips zero-found entries, computes `100 * hit / found`, and records a failure message when actual coverage is below the threshold. `--signoff` suppresses failing status while still returning messages.

Dependencies and integration: uses `Getopt::Long` and `Scalar::Util::looks_like_number`; input schema is the lcov criteria-script JSON summary.

Risks and test signals: missing coverage keys are ignored, which may be desirable for disabled coverage but can hide misconfiguration. The usage text mentions `--suppress` in comments while the implementation uses `--signoff`. Tests should cover threshold boundaries, missing/zero found counts, multiple coverage types, and signoff behavior.
