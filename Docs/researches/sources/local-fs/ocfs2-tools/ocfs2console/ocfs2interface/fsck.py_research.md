# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fsck.py

Runs `fsck.ocfs2` inside an embedded terminal dialog for check or repair workflows.

Key functions:
- `fsck_volume(parent, device, check=False)`
  - Creates `TerminalDialog`.
  - Connects terminal child exit to mark completion.
  - Starts command via idle callback.
  - Prevents closing while fsck is still running by warning the user.
- `start_command(terminal, command, dialog)`
  - Calls `terminal.fork_command`.
- `child_exited(terminal, dialog)`
  - Marks dialog finished.
- `fsck_command(device, check)`
  - Builds:
    - check mode: `fsck.ocfs2 -n '<device>'; sleep 1`
    - repair mode: `fsck.ocfs2 -y '<device>'; sleep 1`
  - Runs through `/bin/sh -c`.

Dependencies:
- `terminal.TerminalDialog`
- `terminal.terminal_ok` exported as `fsck_ok`
- PyGTK/GObject

Notable details:
- Command construction uses shell string interpolation with single quotes around `device`; embedded single quotes in device paths would break quoting.
- Menu availability depends on VTE import success through `fsck_ok`.
