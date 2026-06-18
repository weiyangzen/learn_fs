# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/mtest.c

`mtest` is a command-line SPF macro expansion tester. It accepts optional debug/verbose flags and arguments for macro format, sender, domain, HELO, and IP, then prints `macro()` output.

It initializes IP formatting and defaults `netroot` to `/net`. It is paired with the `testsuite` rc script.
