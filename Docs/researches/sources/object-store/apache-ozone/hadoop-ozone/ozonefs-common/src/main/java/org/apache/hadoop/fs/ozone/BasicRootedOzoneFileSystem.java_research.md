<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneFileSystem.java

## Purpose
Minimal Hadoop `FileSystem` implementation for the rooted Ozone `ofs://` scheme. It maps Hadoop filesystem calls onto Ozone volumes, buckets, keys, snapshots, trash roots, and bucket links while avoiding Hadoop 3-only extension points so it can be shared by compatibility modules.

## Important APIs, types, and functions
The class extends `FileSystem`, creates a `BasicRootedOzoneClientAdapterImpl`, and exposes `open`, `create`, `createNonRecursive`, `rename`, `delete`, `listStatus`, `getFileStatus`, `getContentSummary`, snapshot APIs, `getTrashRoot(s)`, symlink target lookup for bucket links, `setTimes`, and `setSafeModeUtil`. Helper types include `OzoneListingIterator`, `RenameIterator`, `DeleteIterator`, `DeleteIteratorWithFSO`, `DeleteIteratorFactory`, and `OzoneFileStatusIterator`. Conversion is mediated by `FileStatusAdapter`.

## Control flow
`initialize` validates `ofs://authority`, parses OM host/service id and port, builds a canonical URI, determines hsync and datastream settings, creates the adapter, and sets `/user/<shortUser>` as working directory. Read/write methods convert `Path` to Ozone key strings and wrap adapter streams in Hadoop `FSData*Stream`. Rename and delete first classify the `OFSPath` as root, volume, bucket, file, directory, link bucket, or FSO bucket, then either call single adapter operations or iterate prefixed key batches. Listing repeatedly calls adapter `listStatus` with a start key, deduplicating the first element of later pages.

## State and persistence behavior
Local mutable state is configuration-derived: URI, user name, working directory, listing page size, hsync flag, datastream flag, and streaming threshold. Durable mutations happen through the adapter: key create/delete/rename, fake directory marker creation, volume and bucket deletion, snapshot create/rename/delete, and file mtime/atime updates. Recursive content summary performs live tree traversal rather than caching. Fake parent directories are recreated after deletes or renames when object-store directory markers would otherwise disappear.

## Dependencies and integration points
This is the main Hadoop API bridge for OFS. It depends on `OFSPath`, `OzoneFSUtils`, `OzoneClientAdapter`, Ozone OM exceptions and bucket metadata, OpenTelemetry tracing, Hadoop `FileSystem` statistics, Hadoop snapshot/trash/symlink contracts, and Ozone configuration keys for listing and streaming. Full Hadoop 3 subclasses override hooks for storage statistics, token issuers, stream capabilities, and lease recovery.

## Risks and edge cases
Risk concentrates in path classification and recursive iteration. Cross-bucket rename is rejected, root deletion is refused, recursive volume delete is intentionally unsupported, nonrecursive nonempty directory deletion throws, and FSO buckets use different delete/rename paths. Link buckets have POSIX-like trailing slash behavior that determines whether the link or target contents are deleted. Listing pagination depends on `startPath` and duplicate suppression. `pathToKey` rejects invalid names and special-cases `/NONE` in status and setTimes for DistCp. Datastream auto-selection changes stream implementation after a byte threshold, so hsync/capability behavior must remain aligned.

## Test signals
Direct unit coverage in this work item checks default block size, OFS symlink support, snapshot return paths, and OFS path parsing. Broader expected signals come from Hadoop filesystem contract tests, snapshot/trash behavior, link bucket behavior, recursive delete/rename integration tests, stream capability tests, and storage statistics checks in Hadoop 3 modules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneFileSystem.java -->
