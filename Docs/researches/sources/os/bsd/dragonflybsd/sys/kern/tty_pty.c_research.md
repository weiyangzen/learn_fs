# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_pty.c

## Summary
Pseudo-terminal driver implementing Unix98 `/dev/ptmx` cloning plus master/slave pty device behavior. It bridges master I/O to the tty line discipline and supports packet, remote, user-control, and kqueue modes.

## Main Responsibilities
- Clones Unix98 ptys up to `MAXPTYS`, creating `ptm/N` master and `pts/N` slave devices.
- Maintains persistent `struct pt_ioctl` records with open flags, refs, kqueue state, prison ownership, and embedded `struct tty`.
- Implements slave ops: `ptsopen`, `ptsclose`, `ptsread`, `ptswrite`, `ptsstart`, `ptsstop`, `ptsunhold`.
- Implements master ops: `ptcopen`, `ptcclose`, `ptcread`, `ptcwrite`, `ptyioctl`, `ptckqfilter`.
- Supports `TIOCPKT`, `TIOCUCNTL`, `TIOCREMOTE`, `TIOCISPTMASTER`, `TIOCSIG`, and `TIOCEXT`.

## Important Behavior
The master side installs `tp->t_oproc = ptsstart`, `tp->t_stop = ptsstop`, and `tp->t_unhold = ptsunhold`, then raises carrier through the line discipline modem hook. Slave open waits for carrier unless nonblocking.

Unix98 devices are destroyed when both sides are closed and no session references remain; the `pt_ioctl` allocation itself persists. The clone bitmap unit is released during termination.

Remote mode writes master data directly into `t_canq` with a terminating NUL, while normal mode feeds bytes through the active line discipline `l_rint`. Packet and user-control modes prepend control bytes to master reads.

## Risks
Open/close cleanup depends on `pt_refs`, `PF_TERMINATED`, `PF_SOPEN`, `PF_MOPEN`, and `t_refs` interlocking correctly. The file comments note that many routines could use separate locking for `pt` access. Jail/prison ownership is enforced for opens, so credential changes around reused ptys are security-sensitive.
