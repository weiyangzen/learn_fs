# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/privsep.c

## Purpose

Privilege separation for `pflogd`. The privileged parent keeps access to `/dev/bpf` and the log file, while the re-executed child drops privileges, chroots, receives file descriptors, and performs packet processing.

## Process Model

`priv_init()` looks up `_pflogd`. In internal child mode (`-P`), it chroots to the user home, changes to `/`, sets gid/groups/uid to `_pflogd`, assigns fd 3 as the privsep channel, and returns to unprivileged `main()`.

In parent mode, it creates a local socketpair, forks, dup2s the child side to fd 3, re-execs the same program with `-P`, and enters a command loop. The privileged parent forwards ALRM, TERM, HUP, INT, and QUIT signals to the child and sets its process title to `[priv]`.

## Privileged Operations

The command protocol supports:

- `PRIV_INIT_PCAP`: call `init_pcap()`, write BPF buffer size, and pass the BPF fd to the child.
- `PRIV_SET_SNAPLEN`: update the privileged pcap snapshot length and reinstall the filter.
- `PRIV_OPEN_LOG`: open the log file with `O_RDWR|O_CREAT|O_APPEND|O_NONBLOCK|O_NOFOLLOW`, then pass the fd or encoded errno.

Before the loop, the parent unveils resolver config files, `/dev/bpf`, and the selected log file, then locks unveil. A pledge block is present but disabled because BPF ioctls were not pledge-compatible in this code path.

## Child-Side APIs

`priv_init_pcap()` requests BPF initialization, receives the fd, creates a local pcap handle, fills enough internal fields to use the received fd, allocates the pcap buffer, and marks it activated. `priv_set_snaplen()` sends a new snaplen and mirrors it into the child pcap handle on success. `priv_open_log()` requests and receives a log fd.

## IPC Helpers

`may_read()`, `must_read()`, and `must_write()` implement fixed-size blocking transfer loops that retry `EINTR` and `EAGAIN`. The `must_*` functions exit the process on EOF/write failure.

## Risks And Invariants

- The unprivileged child must call these APIs only after `priv_fd` is assigned; the code aborts if called from the privileged side.
- The child reconstructs a pcap handle by assigning libpcap internals directly, which depends on libpcap ABI details.
- The privileged parent exits on unknown commands or pcap initialization failure.
- `unveil(filename, "rwc")` means the selected log path is fixed at startup; later log rotation is handled by reopening that same path.
