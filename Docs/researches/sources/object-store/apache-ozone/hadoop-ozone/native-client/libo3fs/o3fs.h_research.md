# sources/object-store/apache-ozone/hadoop-ozone/native-client/libo3fs/o3fs.h

## Purpose

`o3fs.h` declares the public C API for the libo3fs wrapper.

## Important APIs and Types

- `o3fsFS` and `o3fsFile` are opaque pointer typedefs mirroring libhdfs internal handle types.
- Declares `o3fsConnect`, `o3fsOpenFile`, `o3fsRead`, `o3fsCloseFile`, `o3fsDisconnect`, and `o3fsWrite`.

## Control Flow

No control flow exists in the header. It defines the compile-time contract used by examples and any native clients.

## State and Persistence

No state is stored in the header. Handles represent remote filesystem/file state managed by the implementation and libhdfs.

## Dependencies and Integration Points

The header includes `hdfs.h` for `tPort`, `tSize`, and compatible opaque structs. It is the integration boundary for C clients using Ozone's libhdfs-compatible O3FS access.

## Risks and Edge Cases

Because handle typedefs alias libhdfs internals, ABI compatibility depends on libhdfs. The API is minimal and lacks explicit error retrieval or ownership documentation beyond libhdfs conventions.

## Test Signals

Compilation of examples and consumers against this header is the main signal; ABI smoke tests should link with the implementation and libhdfs.
