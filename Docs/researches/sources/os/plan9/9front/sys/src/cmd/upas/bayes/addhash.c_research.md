# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/addhash.c

`addhash` merges one or more serialized bayes hash tables. Arguments are pairs of `file scale`; each input hash is read with `Breadhash()` and counts are multiplied by the given scale before accumulating into a single `Hash`.

With `-o`, it creates the output file with `DMEXCL`, retrying for up to about two minutes if the file is locked. Without `-o`, it writes the merged hash to stdout.

This is a batch maintenance tool for the older text-hash bayes pipeline.
