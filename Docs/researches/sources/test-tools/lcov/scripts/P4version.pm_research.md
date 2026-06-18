# sources/test-tools/lcov/scripts/P4version.pm

Purpose: Perl version-script callback for lcov/genhtml merges in Perforce workspaces. It maps source paths to Perforce depot revisions and returns stable version strings so coverage data from different source revisions is rejected before line numbers are merged.

Important APIs: package `P4version` exports `new`, `extract_version`, and `compare_version`. `new($script, @args)` parses `--md5`, `--allow-missing`, `--local-edit`, `--prefix`, and an optional depot root. `extract_version($filename)` returns a depot revision, an edited marker with mtime or md5, an md5/mtime fallback, or an empty string for allowed missing files. `compare_version` currently performs exact string inequality.

Control flow and state: construction shells out to `p4 have`, `p4 where`, and `p4 opened`, building an in-memory hash keyed by trimmed path, absolute path, and depot path. Local `add/edit/integrate/delete` states rewrite the stored version when `--local-edit` is allowed.

Dependencies and integration: uses `annotateutil` for modification time and md5, plus `lcovutil::ignorable_error` without an explicit `use lcovutil`, relying on caller environment. It is selected by `tests/common.mak` as `VERSION_SCRIPT` when the test tree is not a git checkout.

Risks and test signals: external `p4` output is parsed with strict regexes and many `die` paths, so Perforce localization, spaces, or changed output formats can break it. Command strings interpolate paths without shell quoting. Tests that run P4-backed coverage or version matching through `common.mak` are the main signals; most local developer runs probably exercise the git version path instead.
