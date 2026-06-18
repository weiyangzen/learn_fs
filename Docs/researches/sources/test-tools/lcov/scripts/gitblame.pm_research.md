# sources/test-tools/lcov/scripts/gitblame.pm

Purpose: loadable git annotation callback that runs `git blame -e` and converts results into the lcov/diffcov annotation tuple format, with optional cache, verification, P4 changelist mapping, and owner abbreviation.

Important APIs: package `gitblame` inherits `AnnotateBase`. `new` accepts `--p4`, `--prefix`, repeated `--abbrev`, `--cache`, `--verify`, `--log`, optional internal domain, and pathname. `annotate_callback($file, $version)` returns `[status, lines, version]` or undef to fall back to filesystem annotation.

Control flow and state: construction extends the base object with P4 mapping, abbreviation regexps, and prefix. Annotation validates readability, changes to the file directory, checks git repository membership with `git rev-parse` and `git ls-files`, then parses `git blame -e`. It normalizes owners, abbreviates by configured substitution regexps, rewrites timestamps to ISO-with-zone format, and optionally maps commits to git-p4 changelists via `git show -s`.

Dependencies and integration: depends on `annotateutil.pm`, `AnnotateBase`, git CLI, `File::Basename`, `File::Spec`, and `lcovutil` through the base class.

Risks and test signals: command strings are unquoted and basename-only blame can be ambiguous with odd filenames. Abbreviation regexps are `eval`ed. Git blame output parsing is strict and may fail on unusual author/date formatting. Test signals include annotate-cache tests, `--verify`, domain abbreviation, git-p4 commit messages, and non-repo fallback.
