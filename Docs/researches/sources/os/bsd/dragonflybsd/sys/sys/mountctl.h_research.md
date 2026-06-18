# File Research: sources/os/bsd/dragonflybsd/sys/sys/mountctl.h

Defines mount control operations, especially journaling control. Public operation constants cover installing/removing/resyncing/status/restarting VFS journals, block journals, export setting, statvfs, and mount flag extraction.

Structures include journal install/restart/remove/status requests, returned journal status, in-kernel `journal_memfifo`, `journal`, `jrecord`, and `jrecord_list`. Kernel APIs create/destroy journal threads and build journal records with nested/leaf data, uio/xio/page/vnode/path/credential helpers. Userland gets `mountctl()`. This header ties `journal.h` protocol records to live mount-level journal management.
