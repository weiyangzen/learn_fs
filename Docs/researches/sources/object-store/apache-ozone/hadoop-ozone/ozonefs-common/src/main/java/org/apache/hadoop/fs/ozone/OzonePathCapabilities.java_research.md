<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzonePathCapabilities.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzonePathCapabilities.java

## Purpose
Shared helper for Hadoop `hasPathCapability` implementations across `o3fs` and `ofs`.

## Important APIs, types, and functions
The static `hasPathCapability(Path,String)` validates arguments through Hadoop `PathCapabilitiesSupport` and returns true for ACLs, checksums, snapshots, and lease recovery.

## Control flow
Capability strings are normalized/validated by Hadoop support code, then matched in a switch. Unknown capabilities return false so callers can fall back to the superclass.

## State and persistence behavior
No state or persistence exists.

## Dependencies and integration points
Full Hadoop 3 `OzoneFileSystem` and `RootedOzoneFileSystem` call this before delegating to `super.hasPathCapability`. It advertises cross-filesystem Ozone features to Hadoop clients.

## Risks and test signals
The helper currently returns a boolean rather than tri-state, so false can mean either unsupported or "let superclass decide" depending on caller convention. Tests should verify every advertised capability and confirm unknown capabilities preserve expected superclass behavior in concrete filesystems.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzonePathCapabilities.java -->
