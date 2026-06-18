# File Research: sources/os/plan9/9front/sys/src/cmd/mk/main.c

Implements the `mk` command entry point, option parsing, environment setup, mkfile parsing, and target dispatch.

Key behavior:
- Parses flags for always-build, debug, explain, mkfile path, ignore/keep-going/no-execute/touch/usage, and what-if timestamps.
- Imports environment, handles command-line variable overrides, sets `MKFLAGS` and `MKARGS`.
- Parses default `mkfile` or each `-f` file.
- Chooses default targets, explicit targets, serial mode, or creates a virtual aggregate target for multiple arguments.
- Initializes execution, catches notes, runs `mk()` for targets, and exits.

Important dependencies: all mk modules, `Binit`, `parse`, `setvar`, `addrules`, `mk`, `timeinit`, `execinit`.

Notable risks:
- Command-line assignments mutate `argv[i][0]` to remove them from target args.
- Multiple explicit targets can become a synthetic virtual rule unless `-s` is used.
