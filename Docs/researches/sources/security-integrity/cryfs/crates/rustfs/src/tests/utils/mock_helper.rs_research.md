# sources/security-integrity/cryfs/crates/rustfs/src/tests/utils/mock_helper.rs

Purpose: helper for setting common mock low-level filesystem expectations and synthetic attrs in tests.

Important APIs: `ROOT_INO`, `TestInodeNumberPool`, `MockHelper::new`, lookup expectation helpers for failure, nonexistence, kind, directory/file paths, and private attr constructors.

Control flow and state: `TestInodeNumberPool` returns increasing arbitrary inodes. Helper methods chain mock `lookup` expectations for each component of a path, returning inode numbers for later expectations. Attribute helpers create directory, file, and symlink `NodeAttrs` with appropriate modes and current timestamps.

Dependencies and integration: used by mkdir tests to establish expected parent and target lookup behavior. Uses `mockall` predicates, path components, common types, and low-level `ReplyEntry`.

Risks and tests: helper-generated attrs use current time and arbitrary sizes, so tests should not depend on exact values unless set. Commented-out helper methods suggest incomplete convenience coverage for direct file/symlink lookup.
