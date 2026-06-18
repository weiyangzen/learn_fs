# sources/sync-backup/borg/src/borg/testsuite/patterns_test.py

Purpose: comprehensive tests for include/exclude pattern classes, pattern-file parsing, matcher ordering, root validation, Unicode normalization, and regex extraction.

Important APIs and control flow: helper `check_patterns` normalizes inputs and compares matched paths. Parametrized suites cover `PathFullPattern`, `PathPrefixPattern`, `FnmatchPattern`, `ShellPattern`, and `RegexPattern` across absolute/relative paths, duplicate slashes, dot segments, separators, wildcards, `**`, hidden files, and raw regex. Unicode tests compare composed/decomposed/invalid latin1 patterns with Darwin normalization behavior. File-loading tests write temporary exclude and pattern files, call `load_exclude_file`/`load_pattern_file`, and evaluate `PatternMatcher`. They cover comments, whitespace, style switches (`p`/`P`), roots (`R`), illegal commands, include/exclude ordering, `parse_pattern` classes/errors, `IECommand` recursion behavior, root path warning validation, and `get_regex_from_pattern`.

State and persistence: creates temporary pattern files and in-memory matchers. Pattern matcher state is ordered; earlier include/exclude decisions affect later matching.

Dependencies and integration points: depends on `borg.patterns`, `ArgumentTypeError`, Python warnings, filesystem temp paths, and `sys.platform` for Darwin normalization. These semantics drive archive creation/extraction filtering.

Risks: include/exclude order is behaviorally significant. Unicode normalization is platform-dependent. Root path validation warns instead of always failing for missing/relative paths, so callers must handle warnings.

Test signals: exact matched path lists, pattern class instances, warning contents, `ArgumentTypeError`/`ValueError`, matcher fallback behavior, and extracted regex strings.
