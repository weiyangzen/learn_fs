# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/sp_common.c

## Purpose
Defines common rump sysproxy protocol structures, framing, send/response-wait helpers, and URL parsing used by sysproxy client/server code via direct `#include`.

## Main Interfaces
Provides static helpers and types for `rsp_hdr`, copy data, syscall responses, fork handshakes, `respwait`, `spclient`, `readframe`, `dosend`, wait-list management, send locking, error mapping, and `parseurl`.

## Control Flow And State
Protocol classes are request, response, and error. Request types include handshake, syscall, copyin/copyout, anonymous mmap, prefork, and raise. Handshake types distinguish guest, auth, fork, and exec.

`dosend` writes an iovec frame with `sendmsg`, handles partial sends by advancing the iovec, polls for output readiness after partial progress, maps `EPIPE`/zero sends to `ENOTCONN`, and uses `MSG_NOSIGNAL`.

Response waits are stored in a per-client TAILQ keyed by request number. `putwait` allocates a request number, inserts a waiter, and reserves the send path; `kickwaiter` finds a matching response frame, transfers the frame body to the waiter, maps protocol errors to errno, and signals the waiter.

`readframe` incrementally reads the fixed header and variable body from a nonblocking socket. Body buffers are allocated with one extra zero byte so string-like bodies are always NUL-terminated.

URL support includes IPv4 TCP and Unix-domain sockets. `tcp_parse` accepts `host:port`, `*`, or `0` for wildcard server bind; client-side wildcard is rejected. `unix_parse` stores absolute cleanup paths for relative socket names when possible. `tcp6` is present but returns `EOPNOTSUPP`.

## Dependencies
Uses sockets, Unix-domain sockets, poll/read/sendmsg, pthread condition variables, queue macros, inet parsing, and optional HOSTOPS overrides for host I/O functions.

## Risks And Notes
Frames trust `rsp_len` enough to allocate body memory after checking only for `>= HDRSZ`; malformed large lengths can force allocation failure/disconnect. Wire data contains host pointers and native scalar layouts, so it is not a portable network protocol. Send-lock state is per client and must be released on every wait/send failure path.
