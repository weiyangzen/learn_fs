# File Research: sources/os/plan9/9front/sys/src/cmd/aux/conswdir.c

Role: Stream filter that notices terminal title/window-directory escape messages and updates Plan 9 window directory state.

Input protocol:
- Recognizes sequences of the form `ESC ] ; path BEL`, chosen to match xterm title setting syntax.
- Removes recognized sequences from the output stream and invokes a helper program, default `/bin/rwd`, with the extracted path.

Behavior:
- Saves and restores `/dev/label` and `/dev/wdir` around execution.
- Streams all non-control input from stdin to stdout.
- Handles interrupts by continuing, while kill notes default.

Implementation details:
- `process` is a small state machine over `None`, `Esc`, `Brack`, `Semi`, and `Bell`.
- Gives up and passes data through if a sequence grows beyond 2048 bytes without completion.
