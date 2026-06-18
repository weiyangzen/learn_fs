# File Research: sources/windows/winfsp/src/dll/launch.c

This file implements client-side launcher communication and launcher registry record management.

Key responsibilities:
- `FspLaunchCallLauncherPipe` / `FspLaunchCallLauncherPipeEx` serialize a command and UTF-16 arguments into the launcher named-pipe protocol, call `FspCallNamedPipeSecurelyEx`, parse success/failure responses, and return launcher Win32 error codes separately from NTSTATUS transport errors.
- `FspLaunchStart`, `FspLaunchStartEx`, `FspLaunchStop`, `FspLaunchGetInfo`, and `FspLaunchGetNameList` are typed wrappers around launcher commands.
- `FspLaunchRegSetRecord` writes or deletes launcher class records under the WinFsp launcher registry key. It handles string fields such as executable, command line, run-as, security, auth package, stderr, and integer fields such as job control, credentials, auth package id, and recovery.
- `FspLaunchRegGetRecord` reads a launcher class record, optionally filters by agent, validates registry types/termination, packs strings into one allocated record buffer, and applies default job-control behavior.
- `FspLaunchRegFreeRecord` frees records allocated by `FspLaunchRegGetRecord`.

Filesystem relevance:
- Launcher records and pipe commands are used by mount/network-provider flows to start and stop managed user-mode filesystems.
- Secret/credential-aware start paths are important for network provider integration.
