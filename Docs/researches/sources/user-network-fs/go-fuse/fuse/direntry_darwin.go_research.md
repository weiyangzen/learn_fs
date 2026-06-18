## sources/user-network-fs/go-fuse/fuse/direntry_darwin.go

Purpose: Darwin-specific layout adapter for parsing raw directory entries.

Important APIs/types/functions: defines platform `dirent` struct and `nameLength` helper for Darwin getdirentries layout.

Control flow: `DirEntry.Parse` uses this platform type to interpret names and record sizes.

State and persistence: stateless struct mapping.

Dependencies and integration: build-tag companion to generic direntry parsing.

Risks and test signals: layout drift causes directory parsing errors on macOS. Directory consistency tests are the main signal.
