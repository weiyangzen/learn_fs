# sources/sync-backup/borg/src/borg/patterns.py

Purpose: parses and evaluates include/exclude patterns from command-line options and pattern files.

Important APIs/types: `PatternMatcher` stores ordered pattern commands plus a fast full-path map. `PatternBase` backs `PathFullPattern`, `PathPrefixPattern`, `FnmatchPattern`, `ShellPattern`, and `RegexPattern`. `IECommand` models include, exclude, exclude-no-recurse, root, and style commands. Parser helpers load files and parse individual command lines. Argparse actions integrate parsing with CLI options.

Control flow/state: pattern-file lines can change fallback style, add roots, or add include/exclude commands. Matcher normalizes paths, checks full-path patterns first, then ordered patterns, updates `recurse_dir`, and returns include/fallback. Pattern objects precompile regexes where useful and increment `match_count` on matches.

Dependencies/integration: uses Borg `shellpattern.translate`, `clean_lines`, argparse helpers, and `Error`. `manifest.py` uses `get_regex_from_pattern` for archive-name matching.

Risks: recursion semantics are subtle; ordinary excludes still recurse so later includes can match beneath them, while no-recurse excludes do not. Full-path include patterns do not contribute to unmatched include counts. Root path validity only warns. User regexes can be expensive or invalid.

Test signals: all pattern prefixes, fallback style switching, command parsing errors, root warnings, recursion behavior, unmatched include reporting, macOS normalization, and archive regex conversion.
