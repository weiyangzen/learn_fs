# File Research: sources/os/plan9/9front/sys/src/9/port/userinit.c

Machine-independent creation of the first user process.

Key responsibilities:
- Includes generated `initcode.i`, the small binary payload that execs `/boot/boot`.
- `userinit()` clears `up`, sets `eve` to the empty string, and starts the `*init*` kernel process.
- `proc0()` initializes process groups, environment/file/root groups, creates root and current directory channels, allocates stack and text segments, copies `initcode` into a text page, then transitions the process from kernel process to normal user process state.
- Calls machine `procsetup()`, `flushmmu()`, and then `init0()` to finish device/env setup and enter user mode.

Dependencies:
- Uses core Plan 9 process, channel, segment, page, and MMU helpers.

Notable behavior:
- The text segment is marked `flushme`, read-only text, while the stack segment is no-exec.
