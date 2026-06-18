# sources/security-integrity/selinux/gui/system-config-selinux

## Purpose
`system-config-selinux` is the privileged launcher for the graphical SELinux administration tool. It runs the Python GUI through PolicyKit.

## Important APIs, types, and functions
The shell script uses `/bin/sh` and a single `exec /usr/bin/pkexec /usr/share/system-config-selinux/system-config-selinux.py`. `exec` makes `pkexec` replace the shell, so the launcher exits with the GUI command status.

## Control flow
Invocation immediately transfers to `pkexec`, which handles authentication and then launches the installed Python GUI. The wrapper has no fallback path.

## State and persistence behavior
The script stores no state. Persistent SELinux changes are made later by the GUI pages after PolicyKit authorization succeeds.

## Dependencies and integration points
It depends on `/usr/bin/pkexec`, a PolicyKit configuration that permits the GUI action, and the installed Python script under `/usr/share/system-config-selinux`. It is the `Exec` target of `system-config-selinux.desktop`.

## Risks and edge cases
If `pkexec` is missing, graphical authentication is unavailable, or the target script is not installed, the launcher fails. Environment variables are filtered by `pkexec`, so the GTK display/session environment must be allowed or reconstructed correctly by policy.

## Test signals
Packaging tests should confirm executable mode and installed paths. Runtime smoke tests should cover successful authorization, canceled authorization, no-display sessions, and missing target script handling.
