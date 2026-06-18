# sources/user-network-fs/rclone/lib/transform/transform_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/transform_test.go -->
## sources/user-network-fs/rclone/lib/transform/transform_test.go

Purpose: high-level tests for path transformation option parsing and tag scoping.

Important APIs and control flow: `newOptions` sets transform options in a background context. Tests check plain path transforms, file-only and dir-only tags on files, all-tag behavior, file-only/dir-only tags on directories, and a table of representative transforms including prefix/suffix/trims, date-like options, truncation, base64, encoding/charmap, case conversion, ASCII stripping, URL escaping, normalization, and regex/command style cases.

State, dependencies, and integration: tests mutate global config in `context.Background()` through `SetOptions`, so they rely on isolated sequential behavior. Dependencies are `context`, `testing`, and testify.

Risks and test signals: good coverage for the public `Path` API and tag behavior. Because it is table-driven over selected cases, it may not catch all parser limitations, regex panic cases, or the segment-slice preallocation issue in every path shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/transform/transform_test.go -->
