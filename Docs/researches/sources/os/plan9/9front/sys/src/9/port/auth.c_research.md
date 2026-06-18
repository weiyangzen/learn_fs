# File Research: sources/os/plan9/9front/sys/src/9/port/auth.c

Portable authentication/user identity helpers and related system calls.

Key behavior:
- Defines global `eve` and `hostdomain`.
- `iseve` checks whether the current process user is the host owner.
- `sysfversion` validates a user version string and negotiates a 9P mount version on a file descriptor via `mntversion`.
- Deprecated `sys_fsession` validates and clears a user buffer for compatibility.
- `sysfauth` validates an auth name, obtains an auth channel through `mntauth`, and returns a close-on-exec fd.
- `userwrite` allows any user to become `none` through the console user device.
- `hostownerwrite` requires `eve`, validates the new owner name, renames users across process/server/share state, updates `eve`, and sets the current process user.
- `hostdomainwrite` requires `eve`, validates and stores the host domain.

Notable dependencies:
- Mount/auth channel operations, fd allocation, process user management, and auth server constants.

Research notes:
- `sysfauth` carefully transfers responsibility for the original channel to the auth channel after `mntauth`.
- Host owner changes propagate through multiple subsystems before replacing the global owner string.
