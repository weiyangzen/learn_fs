# File Research: sources/virtualization/libblockdev/src/plugins/fs/generic.h

Declares generic filesystem plugin APIs, mkfs option structures, feature flags, and capability-query functions.

Key contents:
- Declares signature wiping/cleaning and filesystem-type probing.
- Declares freeze/unfreeze APIs.
- Defines `BDFSMkfsOptionsFlags` and `BDFSMkfsOptions`.
- Declares generic mkfs, resize, repair, check, label, UUID, size, free-space, and min-size APIs.
- Defines resize, configure, fsck, and filesystem feature flag enums.
- Defines `BDFSFeatures`, including partition type metadata and min/max size.
- Declares capability functions such as `bd_fs_can_mkfs()`, `bd_fs_can_resize()`, and `bd_fs_can_get_info()`.

Important invariants:
- `BDFSMkfsOptions` includes reserved padding for ABI stability.
- Feature/capability flags are bitmasks consumed by callers to decide UI/API behavior.
- Generic operation functions accept an optional filesystem type; `NULL` means detect from the device.

Filesystem/block relevance:
- This is the public generic API surface for filesystem operations across supported local filesystems.

Notable risks:
- The declared generic API hides substantial per-filesystem differences, so callers must inspect feature/capability flags before assuming behavior.
