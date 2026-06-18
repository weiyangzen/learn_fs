# File Research: sources/windows/dokany/dokan_fuse/include/old/fuse.h

Compatibility include for older software expecting `<fuse.h>` from a different include layout.

Key contents:
- Documentation comment tells users to prefer `pkg-config --cflags fuse`.
- Includes `"fuse/fuse.h"`.

Role:
- Installed at the include root to forward old include patterns to the modern `fuse/` subdirectory.
