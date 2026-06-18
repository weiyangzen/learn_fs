# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/tryit

Read fully: 29 lines, 584 bytes. SHA-256 prefix: `65d502521297ea2d`.

This is a shell test script for `upas/send` delivery behavior. It prepares test mailbox/forward/pipe files in `/usr/spool/mail`, sends four messages with `mail`, waits, then prints mailbox and pipe-output results.

The cases exercise direct local delivery, forwarding, pipe delivery, and bang-path delivery through `dutoit!bowell!test.local`.

Integration: historical/manual test aid rather than compiled code. It assumes Plan 9 mail paths and commands exist and writes `/tmp/test.mail`.

Risk notes: it mutates real spool paths and uses fixed names. It is not isolated and should only be run in a disposable or test mail environment.
