# sources/test-tools/strace/src/fsmount.c

Decoder for `fsmount`. It prints filesystem context fd, mount flags, and mount attribute flags, returning `RVAL_FD` for the produced mount fd. State is only syscall arguments. Dependencies are `<linux/mount.h>`, `fsmount_flags`, `fsmount_attr_flags`, and fd return formatting. Risks are new mount flags or attribute bits and invalid fd rendering. Tests should cover successful fd returns, common flag combinations, unknown bits, and failed calls.
