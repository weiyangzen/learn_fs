<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbtar -->
# sources/user-network-fs/samba/source3/script/smbtar

## Purpose
Provides the legacy `smbtar` command-line wrapper that turns backup/restore options into an `smbclient` tar-mode invocation against a remote SMB share.

## Important APIs, Types, and Functions
Important routines are `Usage (line 43)`. Key harness variables include `SMBCLIENT (line 19)`, `SMBCLIENT (line 22)`.

## Control Flow
The file is 181 lines and starts with `#!/bin/sh`. Execution begins with command-line parsing/default setup and then performs the requested helper action directly. There are no direct `testit` registrations; success is communicated by the process exit status and stdout/stderr side effects.

## State and Persistence Behavior
It does not maintain durable application state of its own beyond process-local variables and temporary files.

## Dependencies and Integration Points
External command integrations: `smbclient`, `tar`. It is integrated as a source3 utility/helper script rather than a standalone daemon; callers depend on its command-line contract and process exit status.

## Risks
The main risk is environmental coupling: these scripts assume a live Samba selftest layout with valid credentials, paths, daemon state, and helper binaries. The final command uses shell `eval` around user-derived options, so quoting behavior is part of the compatibility surface and must be treated carefully.

## Test Signals
Primary pass/fail signal is the command exit status, with stdout/stderr consumed by the calling harness. Useful regression signals include successful execution of smbclient, tar paths and stable cleanup afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/script/smbtar -->
