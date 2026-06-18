# sources/test-tools/lcov/scripts/gitblame

Purpose: executable wrapper for `gitblame.pm` that formats git blame output for diffcov/lcov annotation callback use.

Important APIs: accepts `gitblame.pm` options such as `--p4`, `--prefix`, `--abbrev`, `--cache`, `--verify`, `--log`, optional domain, and pathname. It imports `gitblame::new` and `annotateutil::call_annotate`.

Control flow and state: if the final argument looks like a file or a non-option path, it calls `call_annotate('gitblame', $0, @ARGV)`, which constructs the class and prints annotation rows. Otherwise it only constructs `gitblame->new` to validate options/help.

Dependencies and integration: adds its own directory to `@INC`, so the module can be used from the source tree or installed support-scripts directory. It is the process callback sibling of the loadable module.

Risks and test signals: the path heuristic treats a final option-like string as constructor-only, so unusual filenames beginning with `-` need `--`-style handling elsewhere. Tests should verify wrapper/module parity, option validation, and actual annotation output via git fixtures.
