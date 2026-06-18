<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryUtil.java

## Purpose
`DirectoryUtil` is a package-private formatting helper for directory paths.

## Important APIs, Types, And Functions
The only method, `pathStr(List<String>)`, renders null as `null` and non-null paths as comma-separated elements inside parentheses.

## Control Flow, State, And Persistence
There is no mutable state or persistence. The method iterates over path components and appends them without escaping or quoting.

## Dependencies And Integration Points
All directory exceptions use this helper to produce path strings; `DirectorySubspace.toString` also uses it.

## Risks And Test Signals
Because components are not escaped, commas or parentheses in path elements can make messages ambiguous. Tests should verify null, empty, single-element, and multi-element formatting because exception messages depend on it.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryUtil.java -->
