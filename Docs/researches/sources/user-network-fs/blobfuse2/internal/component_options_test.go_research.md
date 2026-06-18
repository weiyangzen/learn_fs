## sources/user-network-fs/blobfuse2/internal/component_options_test.go

Purpose: Unit tests for the directory name helper functions in `component_options.go`.

Important APIs and flow: `TestExtendDirName` validates adding a slash to `dir`, preserving `dir/`, and converting empty string to `/`. `TestTruncateDirName` validates removing a trailing slash from `dir/`, preserving `dir`, and converting `/` to empty string.

State and dependencies: No filesystem state. Uses testify suite/assert.

Risks and test signals: Coverage is narrow but directly verifies the edge cases likely to affect directory marker naming. The many option structs in the same source file are data-only and receive no direct tests.
