# sources/test-tools/lcov/scripts/gitversion

Purpose: executable wrapper for `gitversion.pm`, providing process-based lcov `--version-script` behavior.

Important APIs: accepts `--compare old_version new_version filename` or extraction flags `--md5`, `--p4`, `--prefix`, `--allow-missing`, and `--help`. It imports `gitversion::new` and `usage`.

Control flow and state: the wrapper constructs `gitversion->new($0, @ARGV)`, then parses the same options to determine whether this invocation is comparison or extraction. Compare mode exits with `$class->compare_version(@ARGV)`. Extraction prints `$class->extract_version(@ARGV)` and exits zero.

Dependencies and integration: adds the script directory to `@INC` and delegates all substantive behavior to `gitversion.pm`. Used as a standalone callback where loading the module directly is not configured.

Risks and test signals: double option parsing can be brittle and `usage($help)` passes a boolean to a function expecting an executable path. Still, the module constructor does most validation. Tests should exercise wrapper compare/extract parity with `gitversion.pm`, help handling, missing files, md5 fallback, and local-change mode.
