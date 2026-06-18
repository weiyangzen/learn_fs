# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/wrbio.c

Appends an `Acctbio` record to a biography file. It defaults missing fields to empty strings, defaults missing first email to the username, then writes `user|postid|name|dept|email...`.

Used with `rdbio/querybio` account metadata workflows.
