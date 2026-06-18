# sources/user-network-fs/libfuse/lib/cuse_lowlevel.c

`cuse_lowlevel.c` implements the CUSE low-level setup and session bridge for character devices in userspace. It adapts CUSE operation callbacks to generic FUSE low-level callbacks, performs CUSE init negotiation, opens `/dev/cuse`, and runs the selected session loop.

Internal `struct cuse_data` stores copied `cuse_lowlevel_ops`, max read, device major/minor, flags, packed device info length, and flexible `dev_info`. Bridge callbacks ignore inode and forward open/read/write/flush/release/fsync/ioctl/poll to CUSE callbacks. Visible functions are `cuse_lowlevel_new`, `_cuse_lowlevel_init`, `cuse_lowlevel_init`, `cuse_lowlevel_setup`, `cuse_lowlevel_teardown`, and `cuse_lowlevel_main`.

Setup parses options, strips `subtype=`, ensures fds 0-2 are open, creates the session, opens `/dev/cuse`, installs signal handlers, and daemonizes. CUSE init validates protocol major, clamps max write by buffer size, calls user init, replies with `cuse_init_out` plus packed device info, invokes `init_done`, and frees the request. State includes `se->cuse_data`, `se->fd`, connection protocol/max-write values, `se->got_init`, and device identity from major/minor/info strings.

Risks include device-info size overflow, the noted incomplete capability handling for `capable_ext`/`want_ext`, missing `/dev/cuse`, sensitive cleanup ordering around signal handlers/session destruction, and daemonization failures. Test signals include device-info packing limits, callback forwarding, optional callback omission, protocol rejection, max_write clamping, init/init_done ordering, `/dev/cuse` errors, signal/daemonization unwinding, subtype removal, loop selection, and teardown cleanup.
