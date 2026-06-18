# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFile.cc

## Purpose
Provides the out-of-line destructor for the stats file wrapper.

## Important APIs and control flow
The file includes `XrdOssStatsFile.hh`, uses the `XrdOssStats` namespace, and defines `File::~File() {}`. Actual forwarding and timing logic is inline in the header.

## State, dependencies, and integration
The destructor relies on members declared in the header, especially the `std::unique_ptr<XrdOssDF>` that owns the wrapped descriptor. Destruction of the wrapper releases the underlying OSS data-file object through normal C++ member destruction.

## Risks and test signals
Although the destructor is empty, it is a useful ABI anchor for the class. Tests should ensure deleting `File` through an `XrdOssDF` pointer releases the wrapped descriptor exactly once and does not require explicit close beyond normal OSS semantics.
