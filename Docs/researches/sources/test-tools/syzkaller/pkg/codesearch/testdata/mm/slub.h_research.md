# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/slub.h

Purpose: Empty header fixture in a nested source directory.

Important APIs/types/functions: None; zero lines.

Control flow: None.

State and persistence behavior: Its presence validates that `IsSourceFile`/`DirIndex` include `.h` files even when they have no contents.

Dependencies/integration points: Directory indexing and source-file filtering tests.

Risks: Empty headers are not consumed by clangtool's `.c` fixture walker, so behavior is limited to directory/source navigation.

Test signals: Supports directory listing expectations for header files.
