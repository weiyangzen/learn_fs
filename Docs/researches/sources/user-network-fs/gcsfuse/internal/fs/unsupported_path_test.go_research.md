<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/unsupported_path_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/unsupported_path_test.go

Purpose: validates support mode for buckets containing object names with unsupported path components such as duplicate slashes, `.` and `..`, while ensuring supported names remain visible and operable.

Important APIs/types/functions: suite `UnsupportedPathNameTest`; setup config `EnableUnsupportedPathSupport`, `EnableAtomicRenameObject`, `ImplicitDirectories`, and `RenameDirLimit`; tests for read, copy, rename, and delete with unsupported names.

Control flow: setup creates objects containing supported and unsupported path forms, then uses `filepath.Walk`, `cp -r`, `os.Rename`, or `rm -rf` through the mount. Assertions verify only supported names appear and operations complete on the visible subset.

State and persistence behavior: unsupported objects exist in the fake bucket but are filtered from filesystem view. Directory rename/delete operate on the supported visible namespace without failing due to hidden unsupported names.

Dependencies and integration points: exercises directory listing filters, unsupported path support config, atomic object rename, recursive directory rename/delete code, and shell command interoperability.

Risks: hidden unsupported objects can make directory operations appear incomplete or unsafe. Filtering must not hide supported dotfile names such as `.config`, and recursive operations must not accidentally traverse `.` or `..` object keys as real path elements.

Test signals: directory walking shows only supported files/directories, copy copies only supported entries, rename succeeds and visible destination entries are supported only, and recursive delete removes the visible directory without unsupported-name errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/unsupported_path_test.go -->
