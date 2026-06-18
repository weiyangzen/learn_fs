# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdb.c

This is a command-line utility for inspecting or updating a `Msgdb` token database.

With `-c`, it creates the database if needed. With `-i`, it reads tokens or `token count` lines from stdin and increments/replaces stored counts. Without `-i`, it enumerates the database and prints `token value` lines.

It is a thin wrapper around `mdopen`, `mdget`, `mdput`, `mdenum`, `mdnext`, and `mdclose`.
