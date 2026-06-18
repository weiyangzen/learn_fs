# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/plumber.c

`plumber.c` is the daemon entry point. It parses optional rules file and service name, loads `$user` and `$home`, defaults the rules path to `$home/lib/plumbing`, parses rules, then starts the filesystem server in another proc so the main thread can return.

It also provides shared fatal error handling, parse error reporting with input stack context, and checked allocation helpers `emalloc`, `erealloc`, and `estrdup`.
