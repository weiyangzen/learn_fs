# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_socket2.c

## Role

This file implements socket helper primitives: socket-buffer wait/lock support, socket connection-state transitions, listen child creation, wakeups and async notification, socket-buffer reservation/release, default unsupported protocol operations, sockaddr duplication, external socket snapshot export, and socket buffer sysctls.

It complements `uipc_socket.c`: the main file handles high-level socket operations, while this file handles reusable state and buffer mechanics.

## Socket Buffer Sleep And Locking

`ssb_wait()` waits for data or space changes on a `struct signalsockbuf`. It uses atomic `SSB_WAKEUP` and `SSB_WAIT` interlocking so a wakeup racing with sleep setup is not lost. It honors `SSB_NOINTR` by disabling `PCATCH`; otherwise sleeps can be interrupted.

`_ssb_lock()` acquires the logical socket-buffer lock by atomically setting `SSB_LOCK`. If already locked, it sets `SSB_WANT` and sleeps on the flags word. On success it also acquires the socket-buffer token.

`ssbtoxsockbuf()` copies public sockbuf fields into an `xsockbuf` snapshot for sysctl/user export.

## Connection State Transitions

`soisconnecting()` sets `SS_ISCONNECTING` and clears connected/disconnecting state.

`soisconnected()` clears connecting/disconnecting/confirming flags and sets connected state. For sockets on a listen socket's incomplete queue, it either runs an accept-filter callback or moves the child from `so_incomp` to `so_comp`, updates queue lengths and `SS_COMP`/`SS_INCOMP`, wakes the listener, and notifies readers. For ordinary sockets it wakes waiters and both receive/send sides.

`soisdisconnecting()` marks the socket disconnecting and unable to send or receive more, then wakes timeouts, writers, and readers.

`soisdisconnected()` clears active connection flags, marks the socket unable to send/receive and disconnected, drops queued send data, and wakes waiters.

`soisreconnecting()` and `soisreconnected()` reset disconnect state around reconnect attempts.

`sosetport()` assigns the socket's protocol message port.

## Listen Child Creation

`sonewconn_faddr()` creates a child socket for a listening socket. It rejects excessive queue depth, allocates a socket with the listener's protocol, selects the child's protocol port, copies listener type/options/linger/credentials and low-water/timeouts/autosize flags, reserves send/receive buffers, attaches the protocol directly, optionally saves a foreign address, and queues the child on either the incomplete or completed listen queue.

If completed immediately, it sets `SS_COMP` and connection status, optionally `SS_ACCEPTMECH`, and wakes the listener. If incomplete queue length exceeds the configured limit, it aborts the oldest incomplete child before inserting the new one.

`sonewconn()` is the wrapper that does not keep the extra child reference.

## Send/Receive Half-Close And Overflow

`socantsendmore()` sets `SS_CANTSENDMORE` and wakes writers.

`socantrcvmore()` sets `SS_CANTRCVMORE` and wakes readers.

`soroverflow()` records `ENOBUFS` as a receive error and wakes readers when `SO_RERROR` is enabled.

## Wakeups And Message Events

`sowakeup()` handles readiness wakeups for one socket buffer. It atomically checks flags, sets `SSB_WAKEUP`, clears `SSB_WAIT`, wakes sleepers when low-water or closed-side conditions are satisfied, sends SIGIO for async sockets, invokes socket upcalls, triggers knotes, and processes queued `netmsg_so_notify` waiters.

The message-event path uses the socket's pool token because predicates may inspect accept queues. It removes and replies to messages whose predicates are satisfied and clears `SSB_MEVENT` when the list becomes empty.

## Buffer Reservation And Limits

`soreserve()` reserves send and receive buffer space, initializes low-water defaults, and ensures send low-water does not exceed send high-water.

`ssb_reserve()` enforces `sb_max_adj` for user sockets, charges per-UID socket-buffer usage through `chgsbsize()`, calculates `ssb_mbmax` from the efficiency factor, and updates automatic low-water values when `SSB_AUTOLOWAT` is set.

`ssb_release()` flushes queued mbufs and releases reserved socket-buffer space.

`sysctl_handle_sb_max()` updates `sb_max` and recalculates adjusted maximum buffer size, rejecting values below one mbuf plus one cluster.

The file exposes sysctls for maximum socket buffer size, maximum sockets, and socket-buffer waste factor. `init_maxsockets()` initializes `maxsockets` from a tunable and at least the maximum of `maxfiles` and `nmbclusters`.

## Generic Protocol Helpers

`pr_generic_notsupp()` replies `EOPNOTSUPP` for unsupported protocol requests.

`pru_sosend_notsupp()` frees supplied data/control mbufs and returns `EOPNOTSUPP`.

`pru_soreceive_notsupp()` returns `EOPNOTSUPP`.

`pru_sense_null()` fills `st_blksize` from send-buffer high-water and replies success.

## Export Helpers

`dup_sockaddr()` makes a blocking `M_SONAME` copy of a sockaddr. Callers assume success, so it uses `M_INTWAIT`.

`sotoxsocket()` fills an `xsocket` from a live socket: type, options, linger, state, PCB pointer, protocol/family, queue lengths, timeout/error fields, signal process group, OOB mark, send/receive sockbuf snapshots, and credential UID.

## Notable Assumptions And Risks

- `ssb_wait()` and `sowakeup()` form a specific atomic protocol around `SSB_WAIT` and `SSB_WAKEUP`; changing either side can reintroduce lost wakeups.
- Listen sockets are not per-CPU; several comments call out foreign-socket wakeup behavior and the need to hold pool tokens when scanning message predicates.
- `sonewconn_faddr()` relies on exact reference counts after protocol attach, including the extra async receive reference for protocols with `PR_ASYNC_RCVD`.
- `ssb_reserve()` treats kernel sockets differently from user sockets by allowing `RLIM_INFINITY` when no resource limit is supplied.
