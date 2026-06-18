# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceSparseImage.cpp

`DeviceSparseImage` implements Apple sparseimage band mapping. It opens the underlying `DiskImageFile`, handles possible disk-image encryption, reads the sparseimage header node, validates the `sprs` signature, computes logical size and band size, and builds a logical-band-to-file-offset table.

The first header node contributes up to `0x3F0` band IDs; chained index nodes contribute up to `0x3F2` band IDs each. Non-present bands are represented as zero offsets.

`Read()` splits reads across bands, reading present bands from the image file and zero-filling absent bands.

Notable risks: `Read()` computes `chunk = offs >> 20`, hardcoding a 1 MiB band shift even though `m_band_size` is read from the header. `Open()` checks `hdr.signature` inside the index-node loop instead of `idx.magic`, likely a bug.
