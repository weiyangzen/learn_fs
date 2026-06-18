# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/chat.c

Purpose: logging, runtime chat control, and panic handling for 9nfs services.

Key behavior: `chatsrv` publishes a `/srv` control file and forks a shared-memory control process to update `chatty`, `rpcdebug`, and `conftime`. `chat` writes verbose logs, `clog` writes stderr or syslog depending on settings, and `panic` logs and exits.

Integration notes: service files use `chat`/`clog` extensively. Negative/zero `chatty` routes logs through syslog; high chatty levels enable RPC debug.
