# File Research: sources/os/plan9/9front/sys/src/cmd/aux/dial.c

Role: Small dialer that connects to a Plan 9 network address and either runs a command on the connection or pipes stdin/stdout.

Behavior:
- Usage: `dial [-e] [-o msg]... addr [cmd [args]...]`.
- Calls `dial(addr, nil, nil, &cfd)`, writes any `-o` control messages to the connection control fd, then closes it.
- With a command, duplicates the data fd to stdin/stdout and executes the command, trying `/bin/<cmd>` if the direct exec fails.
- Without a command, forks bidirectional copy: child stdin to network, parent network to stdout.
- `-e` makes the child exit cleanly after stdin EOF; otherwise the process pair kills the other side after one transfer direction ends.

Dependencies:
- Uses Plan 9 `dial` and note/postnote process control.
