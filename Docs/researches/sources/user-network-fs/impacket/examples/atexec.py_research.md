# sources/user-network-fs/impacket/examples/atexec.py

## Purpose

`atexec.py` executes a command on a remote Windows host through the Task Scheduler service over DCE/RPC named pipe `\pipe\atsvc`. It creates a temporary scheduled task running as LocalSystem, starts it, optionally captures output through `ADMIN$\Temp`, deletes the task, and cleans up the temporary output file.

## Important APIs, Types, and Functions

`TSCH_EXEC.__init__` stores credentials, Kerberos/hash/AES settings, command, optional session ID, and silent mode. `play(addr)` builds an `ncacn_np` TSCH transport and sets credentials. `doStuff(rpctransport)` contains output decoding, XML escaping, command splitting, DCERPC bind/authentication, task XML generation, registration, run/poll/delete, output retrieval, and cleanup. CLI code parses target, command, codec, keytab, and authentication settings.

## Control Flow

The script parses target credentials and command, optionally loads a keytab, prompts for password if needed, then calls `TSCH_EXEC.play`. `doStuff` connects to TSCH with packet privacy, creates a random task name and temp file name, wraps normal commands in `cmd.exe /C ... > %windir%\Temp\<tmp> 2>&1` unless session or silent mode changes behavior, registers the task XML, runs it, polls `SchRpcGetLastRunInfo` until the task has run, deletes the task, and if output is expected, reads the temp file via the SMB connection and deletes it.

## State and Persistence Behavior

The script mutates the remote host by creating and deleting a scheduled task and, in normal mode, creating and deleting a temp output file under `ADMIN$\Temp`. If cleanup fails, those artifacts can remain. Locally it may load a keytab but writes no files. It prints command output to stdout.

## Dependencies and Integration Points

It depends on Impacket TSCH DCERPC bindings, transport helpers, RPC auth constants, SMB connection access through the transport, target parsing, keytab support, and Windows Task Scheduler behavior on Vista or later.

## Risks and Edge Cases

Remote command execution is inherently high impact. XML escaping is local and must cover command/argument special characters; `-silentcommand` bypasses normal `cmd.exe` wrapping and output capture. The polling loop has no explicit timeout and can wait indefinitely if task status never updates. Output decoding depends on the chosen codec and may need manual code page mapping. Temporary task/file names can collide, though random eight-letter names reduce likelihood. Cleanup tries to delete created tasks in `finally`, but output files can remain on read/delete errors.

## Test Signals

Unit tests can mock TSCH and SMB calls to verify XML generation, escaping, command wrapping, session-id behavior, task cleanup on errors, and output decode fallback. Integration tests require a Windows target and should cover successful output capture, silent command, session run failure, Kerberos/keytab login, hash login, and cleanup after command failure.
