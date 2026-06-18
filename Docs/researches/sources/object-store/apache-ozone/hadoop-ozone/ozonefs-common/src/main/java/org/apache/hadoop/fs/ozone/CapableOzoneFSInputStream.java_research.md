<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSInputStream.java

## Purpose
Hadoop 3 input stream wrapper that advertises Ozone FS read capabilities. It keeps base read behavior in `OzoneFSInputStream` and only adds `StreamCapabilities`.

## Important APIs, types, and functions
The class is package-private and final. `hasCapability` reports support for `READBYTEBUFFER`, `UNBUFFER`, and `PREADBYTEBUFFER`; all other capabilities return false after lowercasing.

## Control flow
Construction passes the wrapped `InputStream` and `FileSystem.Statistics` to the parent. Runtime operations are inherited from `OzoneFSInputStream`; capability checks are local string switches.

## State and persistence behavior
No additional state exists. Reads, seeks, positioned reads, unbuffer, and byte counters are handled by the parent and underlying stream.

## Dependencies and integration points
Created by Hadoop 3/full filesystem subclasses from `createFSInputStream`. It integrates with clients such as `FSDataInputStream.hasCapability`, Hadoop vector/read-buffer APIs, and Ozone key input streams.

## Risks and test signals
The advertised capabilities assume the parent can satisfy byte-buffer and positioned byte-buffer reads for all wrapped inputs. Tests in `TestOzoneFSInputStream` check `READBYTEBUFFER`; additional coverage should include unbuffer and positioned byte-buffer behavior for direct and heap buffers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSInputStream.java -->
