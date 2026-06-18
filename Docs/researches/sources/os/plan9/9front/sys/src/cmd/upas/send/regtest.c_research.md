# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/regtest.c

`regtest` is an interactive Plan 9 regexp tester. It prompts for a regular expression, compiles it, then prompts for lines and prints `yes` or `no` for each match until an empty line.

It is standalone, using only libc, regexp, and bio. There is no mail-specific integration beyond living near rewrite/filter regex code.
