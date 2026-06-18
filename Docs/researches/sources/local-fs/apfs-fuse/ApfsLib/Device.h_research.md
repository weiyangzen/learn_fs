# File Research: sources/local-fs/apfs-fuse/ApfsLib/Device.h

This header declares the abstract block/byte device interface used by APFS container code and tools.

Required virtual methods are `Open`, `Close`, `Read(data, offs, len)`, and `GetSize`. It also provides sector-size accessors and the static `OpenDevice()` factory.

Offsets and lengths are byte-based at this layer; APFS block addressing is handled above by `ApfsContainer`, `ApfsVolume`, or `Dumper`.

The interface is read-only. There are no write, flush, or mutation paths.
