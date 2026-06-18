# sources/sync-backup/bup/lib/bup/cmd/on__server.py

## Purpose
`on__server.py` is the remote helper launched by `bup on`. It receives a length-prefixed argv vector safely over stdin and execs the requested command under `bup mux`.

## APIs and Control Flow
`main(argv)` rejects arguments, reads a 4-byte big-endian size and bounded payload from byte stdin, splits NUL-separated argv, replaces argv[0] with `path.exe()`, and prepends `mux --`. It moves stdin/stdout to fds 3 and 4 for server communication, redirects stdout to stderr for subcommand-visible output, replaces stdin with `/dev/null`, sets `BUP_SERVER_REVERSE`, then `execvp`s bup.

## State, Dependencies, Integration, Risks, Tests
Persistent state is only the environment variable inherited by the execed command. File descriptor reshaping is the main side effect. It depends on exact fd expectations in remote client/server code and mux. Risks include malformed size/payload assertions, fd collision assumptions, stdout/stderr confusion for subcommands, and exec failure returning 99. Test signals include argv framing, size bound, fd 3/4 availability, `BUP_SERVER_REVERSE`, stdin denial, and mux argv construction.
