<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_indentation_issues.py -->
# sources/test-tools/kdevops/scripts/detect_indentation_issues.py

Purpose: scans files for indentation problems, with file-type-specific rules for YAML, Python, Makefiles, and Kconfig. It is part of kdevops style tooling.

Important APIs and functions: `check_file_indentation(file_path)` reads a file as bytes, skips null-containing binary files, decodes UTF-8 with ignored errors, infers early indentation style, and returns issue strings. `main()` accepts explicit paths or defaults to `git diff --name-only`, skips common binary extensions, prints findings, and exits 1 when issues exist.

Control flow: path discovery, per-file filtering, issue collection, summary, and exit code. YAML and Python reject tabs in leading whitespace; Makefile recipes immediately after target lines should start with a tab; Kconfig is intentionally exempt from mixed-indent checks.

State and persistence: read-only; no files are modified.

Dependencies and integration: standard library plus git when no paths are provided. `scripts/style.Makefile` invokes it in style-check flows.

Risks: Makefile recipe detection is simplistic and misses multiline targets, conditionals, and recipes not immediately after a colon. The inferred mixed-indent branch has ineffective comparisons because `uses_tabs`/`uses_spaces` are file-level booleans. Test signals include fixture files for YAML tabs, Python tabs, Makefile recipes, Kconfig help text, binary skip behavior, and git-diff default path discovery.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/detect_indentation_issues.py -->
