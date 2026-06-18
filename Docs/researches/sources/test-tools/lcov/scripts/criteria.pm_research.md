# sources/test-tools/lcov/scripts/criteria.pm

Purpose: reusable criteria callback implementing a simple quality gate: at selected hierarchy levels, the sum of uncovered/lost categories `UNC + LBC + UIC` must be zero for selected coverage types.

Important APIs: package `criteria` exports `new`. `new($script, @args)` accepts `--signoff`, `--function`, `--branch`, and `--mcdc`. `check_criteria($name, $type, $db)` returns `(status, messages)`.

Control flow and state: constructor builds a list of coverage types starting with `line` and appending selected `function`, `MC/DC`, and `branch`. `check_criteria` only evaluates when `$type eq 'top'`; it iterates configured types present in the decoded JSON map, sums `UNC`, `LBC`, and `UIC`, emits messages for non-zero sums, and suppresses nonzero exit status if signoff is enabled.

Dependencies and integration: designed for genhtml `--criteria-script`, either loaded as a Perl module or via the wrapper. Input schema follows lcov criteria-script JSON summaries.

Risks and test signals: coverage type name `MC/DC` must match the host JSON exactly, while threshold-like callbacks elsewhere use `mcdc`. The code ignores non-top levels by design. Tests should cover top-level line-only failure/success, optional branch/function/MC/DC checks, missing keys, and signoff mode.
