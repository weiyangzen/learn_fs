# File Research: sources/os/bsd/dragonflybsd/sys/sys/device.h

DragonFly character-device operation dispatch interface and device creation API.

Key responsibilities:
- Defines generic and per-operation device argument structs for open, close, read, write, ioctl, mmap, mmap_single, strategy, dump, psize, kqfilter, clone, and revoke.
- Defines typed function prototypes for each device operation and `struct dev_ops`, including metadata head and operation vector.
- Defines device type flags such as tape, disk, tty, memory, and seekable set.
- Defines kernel-only driver flags such as memory disk, can-free, track-close, master, no emergency pager, MPSAFE, KVABIO, and quick.
- Defines dev_ops major-number registration/linking structures and RB tree prototypes.
- Declares kernel dispatcher wrappers, dev_ops compile/intercept/restore helpers, device creation/destruction/alias/autoclone APIs, and sync.

Dependencies:
- Kernel-only for most content; includes types, tree, and syslink RPC.
- Uses cdev, ucred, file, uio, bio, knote, vm objects/pages/backing, and sysmsg concepts.

Notable risks:
- `struct dev_ops` field positions are explicitly hard-coded for static initialization.
- `lwkt`/syslink descriptors and dev argument structs form an internal ABI between generic dispatch and drivers.
- Operation wrappers must pass correct file/vnode/credential context for security and lifetime correctness.
