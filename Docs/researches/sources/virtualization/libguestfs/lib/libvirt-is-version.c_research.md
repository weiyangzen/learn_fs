# File Research: sources/virtualization/libguestfs/lib/libvirt-is-version.c

Small command-line helper that checks the runtime libvirt version.

Important behavior:
- Accepts `MAJOR [MINOR [PATCH]]`.
- Initializes libvirt and calls `virGetVersion`.
- Converts the target version to libvirt’s numeric encoding: `major * 1000000 + minor * 1000 + release`.
- Exits success if installed libvirt is greater than or equal to the requested version.
- Uses strict integer parsing for arguments.

Filesystem relevance:
- Build/test helper for enabling libvirt-dependent filesystem appliance launch features conditionally.
