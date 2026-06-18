<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/PathUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/PathUtil.java

## Purpose
`PathUtil` provides public static helpers for creating and manipulating directory path lists.

## Important APIs, Types, And Functions
Methods are `join(List<String>, List<String>)`, `extend(List<String>, String...)`, `from(String...)`, `popFront`, and `popBack`. Outputs are `LinkedList` copies.

## Control Flow, State, And Persistence
All methods are pure in-memory list operations. `popFront` and `popBack` reject empty paths with `IllegalStateException`.

## Dependencies And Integration Points
`DirectoryLayer` uses `popBack` and `join` for parent resolution and absolute path formatting. `DirectorySubspace` uses `join` for partition-relative delegation. Tests and users can build paths with `from` and `extend`.

## Risks And Test Signals
No validation is performed on path component contents or null elements. Tests should cover copy semantics, empty-pop errors, and list order preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/PathUtil.java -->
