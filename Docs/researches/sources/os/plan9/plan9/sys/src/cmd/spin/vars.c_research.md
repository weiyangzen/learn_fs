# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/vars.c

Spin runtime/interpreter variable access and state display module.

Key responsibilities:
- Reads and writes Promela variables in global and local contexts.
- Handles predefined names `_`, `_last`, `_p`, `_pid`, and `_nr_pr`.
- Lazily initializes variable storage and channel instances.
- Casts assigned values to Promela types and reports truncation.
- Dumps global/local variable state for simulation/tracing.

Important functions:
- `getval`/`setval`: dispatch local/global variable access.
- `checkvar`: bounds-checks, declares implicit ints, and initializes arrays/channels.
- `cast_val`: enforces BIT/BYTE/SHORT/UNSIGNED/MTYPE coercions.
- `dumpglobals`/`dumplocal`: print simulation-visible state and optional MSC/track output.
- `dumpclaims`: emits generated x[rs] claim code for channels.

Risks/quirks:
- Reading `_` warns and returns zero.
- Self-referential initializers are rewritten to constant zero.
- Visibility output behavior is controlled by many global flags.
