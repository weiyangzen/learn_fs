# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_run.py

## Purpose
Implements `tahoe run`, starting a client or introducer node in the foreground through Twisted `twistd` machinery while adding Tahoe-specific basedir, pidfile, stdin-close, and startup-error behavior.

## Important APIs, Types, and Functions
Public exports are `RunOptions` and `run`. Helpers include `get_pidfile()`, `get_pid_from_pidfile()`, `identify_node_type()`, `MyTwistdConfig`, `DaemonizeTheRealService`, `DaemonizeTahoeNodePlugin`, and `on_stdin_close()`.

## Control Flow
`RunOptions` parses an optional basedir plus pass-through twistd args. `run()` validates basedir and node type from `*.tac`, constructs `twistd` args with `--nodaemon` and `--rundir`, checks Tahoe's own `running.process` pidfile, registers pidfile cleanup on reactor shutdown, installs an in-memory twistd plugin, and calls `runApp()`. `DaemonizeTheRealService.startService()` schedules actual client/introducer creation when the reactor runs, attaches the resulting service to its parent, maps known config/startup failures to concise stderr messages, and optionally stops the reactor when stdin closes.

## State and Persistence Behavior
Reads node directory contents and `tahoe.cfg` indirectly through client/introducer factories. Uses `running.process` pidfile parsing/checking/cleanup to prevent duplicate node starts. Does not daemonize because `--nodaemon` is always passed.

## Dependencies and Integration Points
Integrates with Twisted `twistd`, Tahoe client and introducer factories via `namedAny`, `HookMixin`, pid utilities, crawler pickle-migration errors, storage-client plugin errors, and node privacy/port assignment validation.

## Risks and Edge Cases
Twistd option pass-through is syntactically constrained: explicit NODEDIR must precede twistd options. Startup uses global/reactor scheduling and late imports, making failure modes asynchronous. Windows skips twistd pidfile disabling. Stdin-close shutdown is convenient for subprocess cleanup but may surprise callers unless `--allow-stdin-close` is used.

## Test Signals
`src/allmydata/test/cli/test_run.py` covers configuration/privacy/port/plugin/crawler migration error rendering, stdin-close behavior, run option parsing, pid checks, and reactor interactions. `test_cli.py` covers run help.
