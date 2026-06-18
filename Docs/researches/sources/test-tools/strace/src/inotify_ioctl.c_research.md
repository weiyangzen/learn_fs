# sources/test-tools/strace/src/inotify_ioctl.c

Ioctl decoder for inotify fds. It handles inotify-specific commands such as `INOTIFY_IOC_SETNEXTWD` when available, printing the next watch descriptor integer from tracee memory. State is tracee memory only. Dependencies are `<linux/ioctl.h>`, inotify ioctl definitions, and generic ioctl return flags. Risks are conditional kernel-header availability and bad pointer behavior. Tests should cover set-next-watch-descriptor ioctl, unknown commands, and invalid pointers.
