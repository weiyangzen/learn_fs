# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/auth.c

cwfs authentication and nvram password support.

The nvram functions read machine auth data, validate the machine key checksum, expose config-device handling, and implement console password checking. The 9P2000 auth-file state machine negotiates `p9sk1`, serves protocol/domain/challenge/ticket-request data, accepts client challenge and ticket+authenticator data, validates tickets with the machine key, maps authenticated server uid, and returns a server authenticator.

`authnew`, `authfree`, `authread`, `authwrite`, `authuid`, `authaname`, and `authuname` are consumed by `9p2.c` auth fids. Authentication state is pooled according to `conf.nauth`.
