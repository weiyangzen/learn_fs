# File Research: sources/windows/dokany/dokan_fuse/pkg-config.pc.in

Template for installing a libfuse-compatible `fuse.pc`.

Key contents:
- Uses configured install prefix, libdir, and includedir.
- Reports name `Dokan FUSE`.
- Describes the library as FUSE API compatibility for Dokan.
- Reports version `2.6.0` to match the advertised libfuse compatibility level rather than Dokan’s own version.
- Emits link flag `-l@PROJECT_NAME@`.
- Emits include path and `_FILE_OFFSET_BITS=64`.

Role:
- Lets existing FUSE build systems discover Dokan FUSE via pkg-config.
