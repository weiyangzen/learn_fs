## sources/user-network-fs/blobfuse2/internal/attribute.go

Purpose: Defines the common object attribute model and property flags used across blobfuse2 components.

Important APIs: `NewDirBitMap`, `NewSymlinkBitMap`, and `NewFileBitMap` construct `common.BitMap64` values for object type flags. Property constants represent unknown, not-exists, directory, empty directory, symlink, and default-mode states. `ObjAttr` carries timestamps, size, mode, flags, path/name, MD5, ETag, and metadata. Methods `IsDir`, `IsSymlink`, and `IsModeDefault` query flags.

State and dependencies: Attribute instances are passed through component APIs, lister/splitter metadata flow, libfuse stat conversion, and external exported aliases. Depends on `common.BitMap64`, `os.FileMode`, and `time`.

Risks: Flags are a shared protocol; mismatched flag constants in external wrappers or components can create subtle behavior changes. `PropFlagEmptyDir` exists but is not exercised in this subset. MD5/ETag are optional and consumers must handle nil values. Tests are indirect through loopback, xload, and component option behavior.
