# File Research: sources/os/bsd/freebsd-src/sbin/conscontrol/conscontrol.c

## Purpose
Lists and changes kernel console configuration, muting, and virtual-console assignment.

## Main Elements
- `consstatus()`: reads `kern.consmute` and `kern.console`, splits configured/available consoles, and prints state.
- `consmute()`: toggles `kern.consmute`.
- `stripdev()`: normalizes `/dev/...` names and rejects other pathnames.
- `consadd()` / `consdel()`: add or remove console devices through `kern.console` sysctl writes.
- `consset()`: uses `TIOCCONS` ioctl to set/unset a virtual console.
- `main()`: dispatches `list`, `mute`, `add`, `delete`, `set`, and `unset`.

## Dependencies And Integration
Uses sysctls and tty ioctls. Device names are expected to refer to entries under `/dev`.

## Risk Notes
Changing console routing affects system logging and console input/output. `consdel()` builds a `-name` command string for the sysctl interface.
