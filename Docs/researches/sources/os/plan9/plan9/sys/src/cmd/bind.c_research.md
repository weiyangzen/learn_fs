# File Research: sources/os/plan9/plan9/sys/src/cmd/bind.c

Plan 9 `bind` command wrapper.

Parses mount flags:

- `-a`: `MAFTER`
- `-b`: `MBEFORE`
- `-c`: `MCREATE`
- `-q`: quiet failure

Requires exactly `new old`, and rejects combining `-a` and `-b`. Calls Plan 9 `bind()`, then reports targeted errors for missing source or target paths before exiting with `bind`.
