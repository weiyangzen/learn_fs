# sources/distributed-fs/xrootd/python/src/ChunkIterator.hh

## Purpose
This header defines an internal Python iterator type used by `File.readchunks()` to stream file data as fixed-size byte chunks.

## Important APIs, Types, and Functions
`ChunkIterator` stores a `File *`, `chunksize`, `startOffset`, and `currentOffset`. `ChunkIterator_init` parses file, offset, and chunk size. `ChunkIterator_iter` returns self. `ChunkIterator_iternext` calls `File::ReadChunk`, returns a Python bytes object, or raises `StopIteration`. `ChunkIteratorType` defines the Python type object.

## Control Flow
Construction converts Python numeric parameters through utility functions. Each iteration reads from the current offset, stops on zero-byte reads, otherwise advances by `chunksize` and returns the actual bytes read. There is no read-ahead or buffering beyond one XrdCl buffer per iteration.

## State and Persistence
Iterator state is in-memory offset progression. It references the `File` object pointer passed by the creator but does not visibly incref it in this header, so lifetime is coupled to the caller retaining the file object.

## Dependencies and Integration Points
Depends on `PyXRootDFile.hh` and `File::ReadChunk`. It is initialized on demand by `File::ReadChunks`.

## Risks and Test Signals
The file pointer lifetime is a risk if a `File` is destroyed while an iterator remains. `currentOffset` advances by requested chunk size rather than actual read size, which is fine for sequential fixed reads until EOF but should be tested for short reads. Tests should cover default 2 MB chunks, explicit offsets, zero-byte EOF, closed file behavior through the caller, and iterator/file lifetime.
