# sources/user-network-fs/samba/source3/smbd/server_exit.c

## Purpose

`server_exit.c` centralizes smbd shutdown and post-fork reinitialization. It provides clean and abnormal server-exit entry points, tears down client connections, sessions, tree connects, global contexts, locking, profiling, and pidfiles, and wraps `reinit_after_fork()` with password database reinitialization for smbd forks.

## Important APIs, Types, And Functions

The main local enum is `enum server_exit_reason` with `SERVER_EXIT_NORMAL` and `SERVER_EXIT_ABNORMAL`. `exit_server_common()` is the `_NORETURN_` implementation behind `smbd_exit_server()` and `smbd_exit_server_cleanly()`. `log_writeable_file_fn()` is a `files_forall()` callback used when `log writeable files on exit` is enabled. `smbd_reinit_after_fork()` calls the generic fork reinit path and then `initialize_password_db(true, ev_ctx)`.

## Control Flow

`exit_server_common()` is guarded by `exit_firsttime` so recursive shutdown exits immediately. It chooses a disconnect status based on clean or abnormal shutdown, removes the global SMBX client from the multichannel registry early, repeatedly returns to root context, disconnects transports, optionally logs writable files, disconnects SMB1 tree connects, logs off all SMBX sessions, frees remaining connection objects, destroys DMAPI session for the parent when compiled, frees `sconn`, closes netlogon credentials DB, dumps profiling, frees global messaging and event contexts, frees smbd memcache, and ends locking. Abnormal shutdown calls `smb_panic(reason)`; normal shutdown logs a notice, removes the smbd pidfile if this is the parent, and exits with code 0.

## State And Persistence Behavior

The function mutates global singleton state: `global_smbXsrv_client`, `global_messaging_context`, `global_event_context`, `smbd_memcache_ctx`, locking state, DMAPI session state, netlogon credentials global DB state, and the parent pidfile. It also disconnects transport/session/tcon state that may have persistent TDB records elsewhere. The writable-file logging path is observational and does not close files directly.

## Dependencies And Integration Points

This file depends on SMBX client/session/tcon APIs, file table traversal, pidfile helpers, profiling, global context free routines, locking teardown, netlogon credential DB management, password DB initialization, and optional DMAPI. It is reached through smbd shim functions, signal/message handlers, child process exits, AIO/IPC send failures, and fatal initialization errors.

## Risks

Shutdown ordering is critical because messaging and event contexts are not direct talloc children of the server connection. Calling transport disconnect after removing the client prevents new multichannel work during teardown. Many cleanup operations log but continue on failure; incomplete tcon/session cleanup may require later cleanupd/scavenger work. Abnormal exits deliberately panic after cleanup, so code paths must avoid calling the abnormal wrapper for normal transport termination. Reentrant exit is flattened to `exit(0)`, which avoids loops but can mask a second failure.

## Test Signals

Tests should exercise clean child exit, abnormal panic path, recursive exit guard, writable-file-on-exit logging, tcon/session cleanup failure logging, pidfile unlink only for parent, and fork reinitialization refreshing passdb state. Integration signals include no leaked global messaging/event contexts after clean exit and expected client disconnect statuses.
