# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsDio.hh

## Purpose
Defines the direct I/O/sendfile interface that an SFS file implementation can use to transfer file data to a client without normal read-buffer copying.

## Important APIs, Types, And Functions
- `XrdSfsDio::SendFile(int fildes)` sends the requested data from one descriptor.
- `XrdSfsDio::SendFile(XrdOucSFVec *sfvec, int sfvnum)` sends a vector of sendfile descriptors, reserving the first vector element for framing.
- `XrdSfsDio::SetFD(int fildes)` switches future processing between read path, fast sendfile path, and descriptor-disabled mode.

## Control Flow
The server learns whether direct I/O should be used through `XrdSfsFile::fctl()` and then passes an `XrdSfsDio` object to `SendData()`. A filesystem either delegates to `SendFile()` once or returns `SFS_OK` without sending so the caller falls back to normal reads.

## State And Persistence
This is an abstract interface. Concrete implementations track whether data has already been sent and which descriptor mode is active. No persistence is defined here.

## Dependencies And Integration Points
Depends on `XrdOucSFVec` for vectorized sendfile operations and integrates with `XrdSfsFile::SendData()` and `SFS_FCTL_GETFD`/`SFS_SFIO_FDVAL` conventions.

## Risks And Edge Cases
The API treats multiple sends for a single request and oversized vectors as logic errors signaled by positive returns. Implementations must return negative values for fatal transport errors so callers close the connection. Descriptor lifetime remains the filesystem's responsibility.

## Test Signals
Mock `XrdSfsDio` implementations should verify single-descriptor sends, vector sends with reserved first element, duplicate-send error handling, negative transport failures, and `SetFD()` mode transitions.
