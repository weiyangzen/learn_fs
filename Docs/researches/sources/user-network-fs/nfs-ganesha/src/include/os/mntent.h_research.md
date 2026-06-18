# sources/user-network-fs/nfs-ganesha/src/include/os/mntent.h

## Purpose
This wrapper normalizes mount table entry APIs for code that reads or writes fstab/mtab-like data.

## Important APIs, Types, And Control Flow
When `LINUX` is set it includes system `<mntent.h>`. When `FREEBSD` is set it includes `<os/freebsd/mntent.h>`. It declares no independent APIs.

## State And Persistence
No state is held in this wrapper. Underlying mount-entry functions read system files or mount databases.

## Dependencies And Integration Points
It insulates common code from Linux/FreeBSD differences in mount table APIs, likely used by export/mount discovery and configuration support.

## Risks And Test Signals
Risks are conditional compilation gaps and semantic differences between `/etc/mtab`, `/proc/mounts`, and FreeBSD mount APIs. Test signals include mount-table parsing on Linux and FreeBSD and builds where only one platform macro is defined.
