# sources/test-tools/strace/src/inotify.c

Decoder for inotify syscalls. It prints fd/path/mask for `inotify_add_watch`, fd/watch descriptor for removal, and flags for `inotify_init1`; `inotify_init` returns fd-formatted output. State is syscall arguments only. Dependencies are `kernel_fcntl.h`, inotify mask/init xlat tables, path printers, and fd return flags. Risks are new mask bits, path pointer failures, and return-value formatting. Tests should cover add/remove, init/init1 flags, unknown masks, bad paths, and failed fd cases.
