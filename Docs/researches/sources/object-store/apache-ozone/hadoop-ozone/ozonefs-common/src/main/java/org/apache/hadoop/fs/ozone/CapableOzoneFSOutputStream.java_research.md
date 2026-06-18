<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSOutputStream.java

## Purpose
Hadoop 3 output stream wrapper that advertises hflush/hsync support for normal Ozone key output streams and deliberately avoids advertising it for EC streams.

## Important APIs, types, and functions
The class extends `OzoneFSOutputStream` and implements `StreamCapabilities`. It unwraps `CryptoOutputStream` before checking the real output stream. `KeyOutputStream` supports `HFLUSH` and `HSYNC` only when hsync is enabled; `ECKeyOutputStream` returns false.

## Control flow
`hasCapability` pulls the `OzoneOutputStream`'s underlying `OutputStream`, unwraps encryption if present, then applies type-specific capability rules. Unknown stream types fall back to `StoreImplementationUtils.hasCapability`.

## State and persistence behavior
Only the hsync-enabled flag is held locally. Persistence and sync semantics remain delegated to the inherited wrapper and Ozone output stream.

## Dependencies and integration points
Used by full Hadoop 3 filesystems. It integrates with encrypted buckets, EC buckets, Hadoop stream capability probing, and the `OzoneFSUtils.canEnableHsync` configuration gate from base filesystem initialization.

## Risks and test signals
The largest risk is over-advertising sync support on EC or encrypted streams. Tests should validate capability results for plain replicated, encrypted replicated, EC, and disabled hsync cases, and should confirm that advertised hsync calls succeed end to end.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSOutputStream.java -->
