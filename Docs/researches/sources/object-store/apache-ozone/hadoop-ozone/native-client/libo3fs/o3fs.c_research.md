# sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs/o3fs.c

## Purpose

`o3fs.c` implements a thin libo3fs wrapper over libhdfs, constructing Ozone `o3fs://` URIs and forwarding file operations to the HDFS C API.

## Important APIs and Functions

- `o3fsConnect(host, port, bucket, vol)` creates an `hdfsBuilder`, sets the namenode URI and port, and connects.
- `o3fsOpenFile`, `o3fsRead`, `o3fsWrite`, `o3fsCloseFile`, and `o3fsDisconnect` cast opaque O3FS handles to libhdfs handles and call corresponding HDFS APIs.

## Control Flow

Connection flow allocates a builder, computes URI length, formats `o3fs://bucket.volume.host` into a stack buffer, sets the URI and port on the builder, and returns `hdfsBuilderConnect`. All other functions are direct one-call wrappers.

## State and Persistence

The wrapper itself stores no global state. Persistent effects are delegated to libhdfs/Ozone: opening, reading, writing, closing, and disconnecting remote filesystem handles.

## Dependencies and Integration Points

It depends on `o3fs.h`, `hdfs.h`, and libhdfs builder semantics. Its URI format integrates Ozone's bucket and volume naming into the host component of `o3fs://bucket.volume.host:port`.

## Risks and Edge Cases

The URI length calculation appears short by one for separators and then calls `snprintf(string, len + 3, ...)` on `char string[len + 2]`, which risks stack buffer overflow. It does not validate null host/bucket/volume inputs. Builder ownership after `hdfsBuilderConnect` is delegated to libhdfs behavior. The wrapper exposes no flush, seek, tell, append, or error-detail APIs.

## Test Signals

Unit or sanitizer tests should cover URI construction length, null handling, and connection failure. Integration tests should verify that wrapper calls behave identically to libhdfs calls for open/read/write/close/disconnect.
