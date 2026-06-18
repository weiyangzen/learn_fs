# File Research: sources/local-fs/dlm/dlm_sand/action.c

This file manages kernel DLM sysfs/configfs state for `dlm_sand`. It creates and removes cluster communication nodes, lockspaces, lockspace members, kernel control attributes, and related runtime kernel settings.

Major paths:
- Sysfs DLM lockspaces: `/sys/kernel/dlm`.
- Configfs cluster root: `/sys/kernel/config/dlm/cluster`.
- Spaces: `/sys/kernel/config/dlm/cluster/spaces`.
- Comms: `/sys/kernel/config/dlm/cluster/comms`.

Key behavior:
- `check_uncontrolled_lockspaces()` detects abandoned kernel lockspaces and fails if any exist.
- `stop_kernel()`, `start_kernel()`, `stop_kernel_leave()`, and `start_kernel_join()` write DLM sysfs control/event/id/nodir attributes.
- `read_configfs_space_members()` loads current configfs membership for a lockspace.
- `add_configfs_lockspace()` creates a lockspace directory.
- `add_configfs_node()` creates a comms node, writes nodeid, binary socket address, optional mark, and local flag.
- `del_configfs_node()` removes a comms node directory.
- `add_configfs_member()` creates a lockspace node directory, writes nodeid, and writes weight from `get_weight()`.
- `del_configfs_member()` removes a lockspace member directory.
- `clear_configfs_comms()`, `clear_configfs_space_nodes()`, and `clear_configfs_spaces()` remove stale configfs state.
- `add_configfs_base()` verifies configfs and DLM configfs are mounted/loaded and creates cluster root if needed.
- `set_configfs_opt()` writes cluster-level options.
- `setup_configfs_options()` clears old state, sets selected DLM options, sets protocol and mark, raises SCTP receive buffers, enables recover callbacks, and sets cluster name `dlm_sand`.
- `setup_misc_devices()` discovers `/proc/misc` minors and waits for `/dev/misc/dlm-control` and `/dev/misc/dlm-monitor`.

Important dependencies:
- Uses `sand_internal.h` for globals, constants, options, lockspace structure, and `do_write()`.
- Uses `config.c` for `get_weight()`.
- Uses logging helpers from `log.c`.
- Kernel ABI assumptions are embedded in sysfs/configfs filenames and binary address write format.

Notable details:
- `add_configfs_node()` treats missing `mark` attribute as non-fatal because older kernels may not support it.
- `set_proc_rmem()` raises `/proc/sys/net/core/rmem_default` and `rmem_max` to 4 MiB for SCTP.
- `find_minors()` has a `found == 3` break condition despite tracking two named devices; harmless but inconsistent.
- Directory member discovery currently trusts directory names as node ids and comments that reading each nodeid attribute would be better.
