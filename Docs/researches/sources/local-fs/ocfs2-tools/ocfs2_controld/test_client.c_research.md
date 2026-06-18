# File Research: sources/local-fs/ocfs2-tools/ocfs2_controld/test_client.c

`test_client.c` is an uninstalled diagnostic client for the `ocfs2_controld` protocol. It connects to the daemon socket and can send fake mount, fake unmount, listclusters, and listfs requests.

The mount path sends `CM_MOUNT`, accepts `CM_STATUS` including `EALREADY`, fakes a successful kernel mount, then sends `CM_MRESULT`. Unmount sends `CM_UNMOUNT`. List operations use the shared receive-list helpers and print returned items.

There is disabled code for deriving UUIDs from mtab/device state. The active tool expects explicit arguments and is useful for daemon protocol testing rather than production mounting.
