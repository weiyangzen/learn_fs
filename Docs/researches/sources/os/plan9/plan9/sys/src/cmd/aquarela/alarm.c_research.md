# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/alarm.c

Provides timer support for NBNS request retry/timeout logic.

Key functions:
- `alarmist` is a process that scans an ordered alarm list, sends on expired channels, and sleeps until the next deadline.
- `nbnsalarmnew` allocates an alarm and buffered channel.
- `nbnsalarmset` cancels any existing placement, computes expiry in milliseconds, inserts by expiry order, and starts/interrupts the alarm process.
- `nbnsalarmcancel` removes an alarm from the list and drains pending channel messages.
- `nbnsalarmend` asks the alarm process to exit.
- `nbnsalarmfree` cancels, frees the channel, and clears the pointer.

Interactions:
- Used by `findname.c` and `addname.c`.

Notable details:
- Uses `QLock` around the global list.
- `threadint` is used to wake the sleeping alarm process when deadlines change.
