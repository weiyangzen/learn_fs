# sources/test-tools/lcov/scripts/p4annotate

Purpose: executable wrapper for `p4annotate.pm`, turning Perforce annotation data into lcov/diffcov callback output.

Important APIs: accepts module options such as `--log`, `--cache`, `--verify`, and a filename. It imports `p4annotate::new` and `annotateutil::call_annotate`.

Control flow and state: mirrors the `gitblame` wrapper. If the last argument is an existing file or non-option path, it calls `call_annotate('p4annotate', $0, @ARGV)` to print annotation records. Otherwise it constructs the module object, primarily for option validation or help.

Dependencies and integration: sets `@INC` to the support-scripts directory and delegates to `p4annotate.pm`. In non-git test environments, `tests/common.mak` points `ANNOTATE_SCRIPT` at `p4annotate.pm,--verify`, not necessarily this wrapper, but the wrapper remains compatible with process callback use.

Risks and test signals: same last-argument heuristic issue as `gitblame`. Test coverage should verify wrapper/module parity, environment validation, and annotation formatting in Perforce workspaces.
