# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCloneSeg.hh

## Purpose
Defines a compact segment descriptor for file clone/copy-range operations.

## Important APIs, Types, And Functions
`XrdOucCloneSeg` contains source file descriptor `srcFD`, reserved integer `reserved`, source offset `srcOffs`, length `srcLen`, and destination offset `dstOffs`, all using fixed-width `uint64_t` for offsets and lengths. The constructor initializes only `reserved` to zero.

## Control Flow
There is no executable logic beyond construction. Callers fill one or more descriptors and pass them to clone-capable storage routines.

## State And Persistence
The struct carries transient operation parameters. It does not own file descriptors or buffers and persists nothing.

## Dependencies And Integration Points
Includes `<cstdint>`. It is a generic utility ABI for modules that support cloning segments from a source descriptor into a destination file.

## Risks And Test Signals
Risks are uninitialized `srcFD`, offsets, and lengths if callers rely on the default constructor, plus future ABI use of `reserved`. Test signals are clone operations with multiple segments, zero-length/large-offset segments, and validation that source descriptors remain caller-owned.
