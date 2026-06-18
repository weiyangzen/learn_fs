# File Research: sources/os/bsd/freebsd-src/sbin/hastd/event.c

`event.c` implements synchronous event messages from HAST workers to the parent daemon.

Key behavior:
- `event_send()` sends an nv header with an event number over `hr_event`, waits for a reply, and frees both nv structures.
- `event_recv()` receives an event in the parent, validates it, maps it to a hook event string, executes the configured hook, and replies with success.
- Recognized events:
  - connect
  - disconnect
  - syncstart
  - syncdone
  - syncintr
  - split-brain
- Receive errors are initially logged at debug level because a worker may have exited normally.

Important details:
- The child waits for the parent’s reply so event delivery is less likely to be lost during immediate worker exit.
- Hook execution uses resource name and role prefix context.
