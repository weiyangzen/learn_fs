# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_pty.c

Implements OpenBSD pseudo-terminal devices: slave side (`pts`), controller/master side (`ptc`), dynamic pty allocation, readiness notification, packet/user-control modes, and `/dev/ptm` allocation.

Major structures and globals:
- `struct pt_softc`: per-pty state containing the tty, flags, read/write selectors, packet/user-control bytes, and master/slave device names.
- `pt_softc`: dynamically grown array of pty softc pointers.
- `pt_softc_lock`: protects the pty array.
- `pts_major`, `npty`, `maxptys`, `tty_gid`: device and allocation metadata.

Allocation and naming:
- `ptyattach()` allocates the initial pty table and ensures ptm support is attached.
- `check_pty()` grows the pty array by powers of two up to `maxptys`, allocates missing softc objects, allocates the backing tty with `ttymalloc()`, and constructs `/dev/ptyXX` and `/dev/ttyXX` names.
- `ptydevname()` maps minor numbers to traditional pty letter/suffix names.
- `pty_getfree()` finds a free pty by checking whether the tty has an output procedure.

Slave side:
- `ptsopen()` initializes tty defaults, waits for carrier unless nonblocking, and opens the current line discipline.
- `ptsclose()` closes the line discipline, closes the tty, and wakes the controller.
- `ptsread()` handles remote mode reads from canonical queue or delegates to the active line discipline.
- `ptswrite()` writes through the active line discipline when the controller is present.
- `ptsstart()` and `ptsstop()` notify the controller of output availability and packet-mode stop/start/flush events.

Controller side:
- `ptcopen()` marks the controller active by setting `t_oproc`, asserts modem carrier through the line discipline, clears external processing, and resets pty mode flags.
- `ptcclose()` drops modem carrier and clears `t_oproc`.
- `ptcread()` reads slave output, packet-mode and user-control headers, and termios state for `TIOCPKT_IOCTL`.
- `ptcwrite()` injects controller input into the slave side, either as remote-mode canonical records or through the active line discipline input function.

Ioctls and modes:
- `ptyioctl()` handles controller-specific behavior for packet mode, user-control mode, remote mode, process group query, signal injection, and master-side `FIONREAD`.
- It delegates to line-discipline and generic tty ioctls, translates break ioctls into user-control notifications when enabled, and emits packet-mode ioctl/start/stop notifications.

Readiness notification:
- Controller kqueue filters report output available for master reads, input capacity for master writes, out-of-band packet/user-control data, and poll/select hangup state.
- `ptcwakeup()` wakes selectors and sleepers on either perspective of the pty pair.

`/dev/ptm`:
- `ptmattach()` locates the pty slave major number.
- `ptmioctl(PTMGET)` allocates two file descriptors, races to open a free master, changes slave ownership/mode when possible, revokes existing slave users, reopens the slave, fills `struct ptmget`, and installs both vnode-backed files into the descriptor table.
- `ptm_vn_open()` is a constrained vnode open helper using temporary root credentials for pty nodes.

Filesystem/storage relevance:
- Strong character-device/VFS relevance: the `PTMGET` path opens and installs master/slave vnodes, updates vnode timestamps, changes slave ownership and mode, revokes aliases, and coordinates file-descriptor insertion for pty allocation.
