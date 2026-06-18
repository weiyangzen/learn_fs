# File Research: sources/os/bsd/freebsd-src/sbin/hastd/control.h

`control.h` declares HAST control-plane entry points and worker command IDs.

Key contents:
- Worker control commands:
  - `CONTROL_STATUS`
  - `CONTROL_RELOAD`
- Declares:
  - `child_cleanup()`
  - `control_set_role()`
  - `control_handle()`
  - `ctrl_thread()`

This header is shared by parent daemon code and worker-role code.
