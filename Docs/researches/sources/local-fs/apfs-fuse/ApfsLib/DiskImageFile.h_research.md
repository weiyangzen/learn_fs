# File Research: sources/local-fs/apfs-fuse/ApfsLib/DiskImageFile.h

This header declares `DiskImageFile`, a read-only file wrapper with optional encrypted-DMG decoding.

Public API includes open, close, reset, byte-range read, content-size accessor, and encryption setup detection.

Private methods implement v1/v2 encryption setup and PKCS unpadding. Private state includes the image stream, encryption flag, encrypted-content offset/size/block size, HMAC key, and AES context.

It is used by `DeviceDMG` and `DeviceSparseImage` as the underlying byte source.
