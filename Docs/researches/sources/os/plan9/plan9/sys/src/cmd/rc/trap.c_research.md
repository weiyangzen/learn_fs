# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/trap.c

rc trap delivery logic.

`dotrap()`:
- Processes pending `trap[]` counters while `ntrap` is nonzero.
- For child processes, exits immediately with current status.
- Looks up function variables named by `Signame[]`.
- If a trap function exists, starts it with copied `$*` as a local and clears redirection inheritance.
- If no function exists for interrupt/quit, unwinds to the interactive command loop.
- Otherwise exits.

Risk/notes:
- Trap functions run as ordinary rc function code on the interpreter stack.
- `$*` is copied from the interrupted context.
