<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixOzoneFileSystem.java

## Purpose
POSIX-oriented `o3fs` variant that forces create semantics compatible with clients expecting an existing inode-like file before writing.

## Important APIs, types, and functions
Extends `OzoneFileSystem` and overrides `create(Path, FsPermission, boolean, int, short, long, Progressable)`.

## Control flow
`create` calls `super.create`, immediately closes the returned stream, then calls `super.create` again and returns the second stream. This creates/closes an initial empty file before opening the actual write stream.

## State and persistence behavior
The first create persists an empty key and close metadata; the second create overwrites/reopens according to inherited create semantics. This doubles create-side effects.

## Dependencies and integration points
Used where pseudo-POSIX create behavior is configured for bucket-scoped Ozone FS.

## Risks and test signals
The double-create can produce extra metrics, extra OM operations, and failure modes if overwrite is false or the first close succeeds but the second create fails. Tests should cover overwrite true/false, failure cleanup, and observable metadata after interrupted second create.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixOzoneFileSystem.java -->
