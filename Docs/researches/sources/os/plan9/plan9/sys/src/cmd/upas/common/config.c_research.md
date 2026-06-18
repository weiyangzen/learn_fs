# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/config.c

- Role: Defines default upas filesystem paths and mailbox mode.
- Values: `MAILROOT=/mail`, `UPASLOG=/sys/log`, `UPASLIB=/mail/lib`, `UPASBIN=/bin/upas`, `UPASTMP=/mail/tmp`, `SHELL=/bin/rc`, `POST=/sys/lib/post/dispatch`, `MBOXMODE=0662`.
- Integration: Referenced through `sys.h` by common utilities and mail tools.
