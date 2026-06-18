<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/package-info.java

## Purpose
This package descriptor documents the directory layer as tools for managing hierarchical key subspaces.

## Important APIs, Types, And Functions
The file exports package Javadoc only. It describes paths as tuples/lists of strings, directory-associated subspaces, short prefixes, and links to general directory documentation.

## Control Flow, State, And Persistence
No runtime code executes here. The documented state model is path-to-prefix metadata plus content subspaces managed by `DirectoryLayer`.

## Dependencies And Integration Points
The descriptor frames `Directory`, `DirectoryLayer`, `DirectorySubspace`, and `DirectoryPartition` for generated API docs.

## Risks And Test Signals
Risk is documentation drift around path representation and partition behavior. Javadoc generation and link validation are the main direct signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/package-info.java -->
