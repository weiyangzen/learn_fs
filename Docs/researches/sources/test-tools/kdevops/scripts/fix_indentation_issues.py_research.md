<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/fix_indentation_issues.py -->
# sources/test-tools/kdevops/scripts/fix_indentation_issues.py

Purpose: modifies files to correct simple indentation issues for YAML, Python, and Makefile recipe lines.

Important APIs and functions: `fix_file_indentation(file_path, dry_run=False)` skips null-containing binaries, determines file type, converts leading tabs to four spaces for YAML/Python, and converts leading spaces to tabs for recipe lines immediately following Makefile targets. `main()` accepts paths or defaults to all `git ls-files`, supports `--dry-run`, and prints totals.

Control flow: parse CLI, discover paths, filter missing/non-file/common binary suffixes, call fixer per file, write modified content when not dry-run, return 0.

State and persistence: rewrites modified files in binary mode using UTF-8 encoded content; dry-run only reports counts.

Dependencies and integration: standard library plus git for default all-tracked-file mode. `scripts/style.Makefile` calls the whitespace fixer directly; this indentation fixer is available for manual remediation.

Risks: all tracked-file default is broad and could rewrite many files. Makefile recipe detection is oversimplified. UTF-8 decode with ignored errors can drop undecodable bytes in rewritten files. The print order reports line changes before file headers, which is awkward for logs. Test signals include dry-run invariance, YAML/Python tab conversion, Makefile recipe fixtures, binary skip, and non-UTF-8 file protection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/fix_indentation_issues.py -->
