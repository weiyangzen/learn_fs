# sources/test-tools/syzkaller/vm/isolated/isolated.go

## Purpose

`isolated.go` implements a VM backend for externally managed physical or virtual machines reachable over SSH. It repairs/reboots targets, copies binaries to a target directory, runs commands remotely, captures remote console output, and optionally reads pstore crash logs.

## Important APIs, Types, and Functions

Key types are `Config`, `Pool`, and `instance`; the backend registers as `isolated`. Important functions include `ctor`, `Pool.Count`, `Pool.Create`, `Forward`, `ssh`, `waitRebootAndSSH`, `repair`, `waitForSSH`, `waitForReboot`, `Close`, `Copy`, `Run`, `readPstoreContents`, `Diagnose`, and `splitTargetPort`.

## Control Flow

`ctor` loads config, defaults host to localhost, validates targets and optional USB device counts. `Create` parses target host/port, repairs the target, remounts root writable, creates and cleans the target directory, and clears pstore when enabled. `repair` waits for SSH, optionally reboots through USB authorization toggling or SSH, then runs a startup script by reading it locally and executing its contents remotely. `Run` opens remote console output, starts SSH command execution in the target directory with optional port forwarding, and multiplexes dmesg/stdout/stderr.

## State and Persistence Behavior

Instance state tracks SSH options, target index, close channel, forward port, OS, and timeout scale. It mutates remote machines by rebooting, remounting `/`, deleting target directory contents, killing old binaries before copy, running startup scripts, and optionally deleting pstore files. USB reboot mutates host sysfs authorization files.

## Dependencies and Integration Points

It depends on SSH/SCP, `vmimpl.OpenRemoteConsole`, `vmimpl.Multiplex`, target OS metadata, optional pstore support, and `vmimpl.EscapeDoubleQuotes` for startup script execution.

## Risks and Test Signals

String-built shell commands make quoting important. `ssh` has a hard 30-second command wait outside some longer boot waits. USB power toggling requires exact sysfs device numbers. Tests cover double-quote escaping and target:port parsing; integration coverage should include repair paths, startup scripts, copy/run, forwarding, pstore diagnosis, and system SSH config behavior.
