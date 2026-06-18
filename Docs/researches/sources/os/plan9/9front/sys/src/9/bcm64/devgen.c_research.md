# File Research: sources/os/plan9/9front/sys/src/9/bcm64/devgen.c

Architecture-local directory generation helper.

Key responsibilities:
- Implements `devgen()` wrapper behavior for directory table walking.
- Supports generated device directory entries using Plan 9 `Dirtab` metadata.

Role:
- Small compatibility helper for device file enumeration in this ARM64 port.

Dependencies:
- Plan 9 `Chan`, `Dirtab`, `Dir`, and device directory helpers.
