<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSDataStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSDataStreamOutput.java

## Purpose
Hadoop 3-capable wrapper for Ozone datastream output. It adds `StreamCapabilities` to `OzoneFSDataStreamOutput` while keeping the base stream usable in Hadoop 2 modules that cannot reference the capability interface.

## Important APIs, types, and functions
The constructor accepts an existing `OzoneFSDataStreamOutput` and hsync-enabled flag, reuses the wrapped `ByteBufferStreamOutput`, and implements `hasCapability`. Capability checks are meaningful only when the wrapped stream is a `KeyDataStreamOutput`; `hflush` and `hsync` report true only when hsync is enabled.

## Control flow
`hasCapability` lowercases the requested capability and delegates to `hasWrappedCapability`. Unknown capabilities, non-key datastream implementations, and disabled hsync all return false.

## State and persistence behavior
The only state is the boolean hsync capability flag. Durable writes and flushes are handled by the inherited datastream wrapper and underlying Ozone client stream.

## Dependencies and integration points
Used by Hadoop 3/full `OzoneFileSystem` and `RootedOzoneFileSystem` hooks when datastream output is selected by the filesystem threshold logic. It depends on Hadoop `StreamCapabilities`, HDDS `ByteBufferStreamOutput`, Ozone `KeyDataStreamOutput`, and Hadoop `StringUtils`.

## Risks and test signals
The main risk is a mismatch between advertised hsync/hflush support and actual stream behavior, especially if new datastream output classes are introduced. Stream capability assertions should cover both enabled and disabled hsync and datastream vs non-datastream wrapped outputs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSDataStreamOutput.java -->
