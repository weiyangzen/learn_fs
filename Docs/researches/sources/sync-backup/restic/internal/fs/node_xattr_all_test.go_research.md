# sources/sync-backup/restic/internal/fs/node_xattr_all_test.go

Purpose: Cross-platform xattr restore/fill tests for platforms with xattr support, including Windows.

Important APIs: `setAndVerifyXattr`, `setAndVerifyXattrWithSelectFilter`, `TestOverwriteXattr`, and `TestOverwriteXattrWithSelectFilter`.

Control flow and state: Tests restore xattrs onto a temp file, read them back into a node, and compare expected names/values. Filter tests simulate `--include-xattr` patterns and confirm only selected attributes are restored while old selected-but-unexpected attrs are removed.

Dependencies and integration: Uses `filter.IncludeByPattern` for selection and adapts names to uppercase on Windows.

Risks: Platform xattr naming and filesystem support differ; Windows case-insensitivity is explicitly handled.

Test signals: Confirms xattr overwrite semantics and filter-driven restore behavior across supported platforms.
