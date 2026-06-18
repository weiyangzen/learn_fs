# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/Ccli.c

Small command-line dispatcher used by fossil's interactive console.

It registers named commands in a dynamically grown table, tokenizes input lines, ignores empty lines and comment lines starting with `#`, finds the matching command, runs it, and prints the current Venti/fossil error string on failure. `cliError` formats an error into `vtSetError`.

This is the shared execution path for console commands registered by the 9P, fsys, srv, user, and diagnostic modules.
