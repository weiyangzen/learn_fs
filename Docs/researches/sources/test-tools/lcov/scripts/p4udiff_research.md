# sources/test-tools/lcov/scripts/p4udiff

Purpose: generates a unified diff between two Perforce changelists, labels, or a baseline and current sandbox state, including optional unchanged-file markers for differential coverage.

Important APIs/types: internal `P4File` parses `p4 files`/`p4 opened` descriptions and exposes `path`, `name`, `rev`, `action`, `changelist`, and `type`. `P4FileList` stores included non-binary files with `append`, `files`, `get`, `remove`, and `include_me`. CLI usage is `p4udiff [--include/--exclude] [-b] [--no-unchanged] sandbox_directory base current`.

Control flow and state: the script maps sandbox to depot path with `p4 where`, builds baseline and current file lists, adjusts current state for `sandbox` by querying `p4 opened`, computes a union with presence states, streams `p4 diff -du`, rewrites depot paths to sandbox paths, filters hunks, then emits synthetic sections for unchanged, deleted, and added files using `p4 print` or local file content.

Dependencies and integration: depends on P4 CLI, `DateTime` import, regex include/exclude filters, and unified diff conventions consumed by lcov/genhtml differential reports.

Risks and test signals: command strings are often unquoted, `p4 where` parsing assumes three whitespace-separated fields, and binary files are dropped. The `-b` flag is parsed but not incorporated into the diff command. Tests require Perforce fixtures for changed/deleted/added/sandbox cases and should validate unchanged suppression.
