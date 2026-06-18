<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSOutputStream.java

## Purpose
OutputStream and `Syncable` wrapper for Ozone `OzoneOutputStream`.

## Important APIs, types, and functions
Implements `write(int)`, `write(byte[],int,int)`, synchronized `flush`, synchronized `close`, `hflush`, `hsync`, and a protected `getWrappedOutputStream` accessor.

## Control flow
Writes and flush/sync operations are delegated to the Ozone stream under tracing spans. `hflush` maps to `hsync`, and `close` delegates directly.

## State and persistence behavior
The only local state is the wrapped output stream. Persistent data and metadata are created by the Ozone client stream when bytes are written, synced, and closed.

## Dependencies and integration points
Created by adapter `createFile`, wrapped in Hadoop `FSDataOutputStream`, and further wrapped by Hadoop 3 `CapableOzoneFSOutputStream`. It participates in tracing and hsync support.

## Risks and test signals
Risk is low but lifecycle-sensitive: close errors must propagate and sync capability must match the actual wrapped stream. Tests should verify write content, flush/hsync propagation, close behavior, and encrypted/EC stream handling through the capable wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSOutputStream.java -->
