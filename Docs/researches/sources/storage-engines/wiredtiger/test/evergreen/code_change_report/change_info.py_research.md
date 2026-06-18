<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/change_info.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/change_info.py

Purpose: defines the small data carrier used by code-change report tooling to represent one parsed diff hunk. `ChangeInfo` stores `status`, `new_file_path`, `old_file_path`, `new_start`, `new_lines`, `old_start`, `old_lines`, and raw pygit2 hunk `lines`.

APIs and dependencies: the only public API is `ChangeInfo.__init__`. It has no imports and no validation; callers are expected to supply values copied from `pygit2.Patch` and `pygit2.Hunk` objects.

Control flow and state: construction is a direct assignment of fields. Instances are transient in-memory objects created by `code_change_helpers.diff_to_change_list()` and consumed by `code_change_info.py` and `per_test_code_coverage_report.py`.

Integration points: the fields mirror pygit2 diff metadata and become JSON in downstream report builders. `lines` remains a list of pygit2 line objects until later converted into serializable dictionaries.

Risks and test signals: because there is no type enforcement or normalization, downstream code assumes the hunk/line objects expose `content`, `new_lineno`, and `old_lineno`. Renames are represented by both old and new file paths, but dictionary consumers key primarily by new path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/change_info.py -->
