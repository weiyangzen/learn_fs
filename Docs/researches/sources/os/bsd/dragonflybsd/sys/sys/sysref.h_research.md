# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysref.h

System resource registration and reference-management definitions.

Key contents:
- Defines callback types for terminate, lock, and unlock operations.
- Defines `struct sysref_class`:
  - resource name
  - malloc type
  - RPC protocol id
  - embedded sysref offset
  - object size
  - cache sizing
  - flags
  - object cache hooks
  - resource operation callbacks
- Defines embedded `struct sysref`:
  - per-CPU RB-tree node
  - machine-wide `sysid_t`
  - reference count
  - flags
  - resource class pointer
- Defines flags:
  - `SRC_MANAGEDINIT`
  - `SRF_SYSIDUSED`
  - `SRF_ALLOCATED`
  - `SRF_PUTAWAY`
- Defines `SYSREF_PROTO_*` protocol numbers for vmspace, vnode, process, LWP, fd, socket, mount, device, and related resources.
- Declares `allocsysid()` for kernel builds.

Important behavior:
- Resources are backed by `objcache`.
- The owning CPU is encoded through the SYSID/RB-tree association.
- Negative refcounts represent construction/deconstruction states.
- Reusing SYSIDs can avoid RB-tree relocation when resources are not looked up via syslink.

Research notes:
- This header establishes the generic identity/reference substrate for major kernel resources.
- `sysref2.h` supplies the inline refcount operations.
