# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgclass.c

`msgclass` is a newer database-backed message classifier. It reads token/count files, loads one or more class databases supplied with `-d name dbfile`, computes the most discriminating tokens, and prints the selected class plus per-class probabilities and token evidence.

Options include `-a` to add the current message tokens to the selected class database, `-l` to hold a lock file while updating, `-m` update multiplier, and `-t` confidence threshold. It uses `Msgdb` from `msgdbx.c`.

Notable implementation issue: in `lockfile()`, the condition `if(strstr(err, "file is locked")==nil && strstr(err, "exclusive lock")==nil))` has an apparent extra closing parenthesis in the source as read, which would be a compile error unless hidden by build-time differences.
