# sources/test-tools/lcov/scripts/p4annotate.pm

Purpose: loadable Perforce annotation callback with cache/log/verify support. It runs `p4 annotate`, merges local edits from `p4 diff`, and returns per-line owner/date/changelist metadata.

Important APIs: package `p4annotate` inherits `AnnotateBase`. `new($script, @args)` accepts `--verify`, `--log`, `--cache`, and `--help`, and validates `P4USER`, `P4PORT`, and `P4CLIENT`. `annotate_callback($pathname, $computed_version)` returns `[status, lines, version]` or undef for filesystem fallback.

Control flow and state: symlink paths are resolved manually. If `p4 files` confirms repository membership, the module reads `p4 have` for revision, checks `p4 opened` for local edit/integrate, parses `p4 diff` normal diff output into `%localAdd` and `%localDelete`, then streams `p4 annotate -Iucq` and interleaves local additions/deletions with depot annotation lines. Local additions are attributed to `P4USER` and file mtime.

Dependencies and integration: depends on `annotateutil`, `AnnotateBase`, Perforce CLI, and callback host globals through the base class.

Risks and test signals: Perforce output parsing is strict and assumes normal diff format. Timezone is hard-coded to `-05:00` for P4 dates. Shell command paths are unquoted. Local delete/add line tracking can die on unexpected diff shape. Tests should cover plain annotate, local edit merge, cache/verify, symlink resolution, and non-repo fallback.
