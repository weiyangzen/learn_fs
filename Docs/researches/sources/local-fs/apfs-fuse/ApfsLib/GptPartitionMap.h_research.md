# File Research: sources/local-fs/apfs-fuse/ApfsLib/GptPartitionMap.h

This header declares the `GptPartitionMap` helper class. It exposes construction, `LoadAndVerify(Device&)`, `FindFirstAPFSPartition()`, `GetPartitionOffsetAndSize()`, and `ListEntries()`.

Internally it owns a CRC32 object, raw backing buffers for the GPT header and entries, typed pointers into those buffers, and the detected sector size. The GPT structs themselves are forward-declared here and defined privately in the `.cpp`, keeping callers independent of the on-disk GPT layout.

This class is used by APFS utilities before constructing an `ApfsContainer`, allowing a whole-disk image to be converted into the byte range of the first APFS partition.
