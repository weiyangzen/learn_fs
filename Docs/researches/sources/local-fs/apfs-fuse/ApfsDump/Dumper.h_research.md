# File Research: sources/local-fs/apfs-fuse/ApfsDump/Dumper.h

This header declares the `Dumper` class used by `ApfsDump/Apfs.cpp`. Public API is `Initialize()`, `DumpContainer(std::ostream&)`, and `DumpBlockList(std::ostream&)`.

The class stores raw `Device*` handles for main and tier2 devices, partition base/size fields, dynamic APFS block size, AES-XTS state, and an encryption flag. It also exposes no ownership semantics, so callers retain responsibility for device lifetime.

Private helpers cover physical reads, vector-backed reads, optional decryption, and checkpoint-map OID lookup. It imports `Crypto/AesXts.h` and declares `extern volatile bool g_abort`.

The header is tightly coupled to APFS disk structs through private signatures using `checkpoint_map_phys_t` and `checkpoint_mapping_t`, even though `DiskStruct.h` is not included directly here in the visible file.
