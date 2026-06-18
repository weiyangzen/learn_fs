<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryAlreadyExistsException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryAlreadyExistsException.java

## Purpose
This exception identifies attempts to create or move a directory to a path where a directory already exists.

## Important APIs, Types, And Functions
`DirectoryAlreadyExistsException` extends `DirectoryException` and has a package-private constructor taking a `List<String>` path. It fixes the base message to `Directory already exists`.

## Control Flow, State, And Persistence
The class is thrown by directory create/open logic when `allowOpen` is false and an existing node is found, and by move when the destination node already exists. It stores the offending path through the superclass.

## Dependencies And Integration Points
It depends on `DirectoryException` for path formatting and on `DirectoryUtil.pathStr` through the superclass. It is part of the public exception hierarchy named by `Directory.create` and `Directory.move` docs.

## Risks And Test Signals
The constructor is package-private, so tests generally observe it through `DirectoryLayer` operations. Test signals include duplicate create, move onto existing directory, and async exceptional completion preserving the path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryAlreadyExistsException.java -->
