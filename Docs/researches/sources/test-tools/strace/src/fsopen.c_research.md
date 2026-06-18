# sources/test-tools/strace/src/fsopen.c

Decoder for `fsopen`. It prints filesystem name and flags from `fsopen_flags`, returning fd-formatted results. No persistent state is used. Dependencies are `<linux/mount.h>`, string printers, xlat flags, and syscall return flags. Risks are null or inaccessible fs names and new open flags. Tests should cover known filesystems, bad pointers, unknown flags, and success/failure fd returns.
