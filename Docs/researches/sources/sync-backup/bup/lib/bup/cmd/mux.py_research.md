# sources/sync-backup/bup/lib/bup/cmd/mux.py

## Purpose
`mux.py` runs a subcommand and multiplexes its stdout and stderr into bup's framed stream protocol. It is paired with `demux.py` for remote command execution.

## APIs and Control Flow
`main(argv)` duplicates original stdin, replaces fd 0 with `/dev/null` while parsing options, requires a command, creates stdout/stderr pipes, spawns the subcommand with original stdin and pipe outputs, writes the `BUPMUX` header to stdout, and calls `helpers.mux` to frame both output streams. It waits for the child and exits with the child's status.

## State, Dependencies, Integration, Risks, Tests
State is process/file-descriptor state only. It depends on `Popen`, `stopped`, `byte_stream`, `helpers.mux`, and exact fd inheritance behavior. It integrates with `on__server.py`, which prepends `mux --` to remote argv, and `demux.py`, which consumes the framed stream. Risks include descriptor leaks from `close_fds=False`, protocol header mismatch, subcommand stdin ownership, and timeout behavior in `stopped`. Test signals include stdout/stderr interleaving preservation, child exit propagation, missing command fatal, and stdin redirection semantics.
