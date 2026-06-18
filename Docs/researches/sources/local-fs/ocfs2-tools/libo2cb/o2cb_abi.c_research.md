# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb_abi.c

## Purpose

Implements the userspace/kernel ABI for O2CB and alternate OCFS2 cluster stacks. It manages cluster stack detection/setup, configfs cluster/node/heartbeat entries, heartbeat reference counting, userspace control daemon communication, control-device handshakes, and runtime cluster descriptor discovery.

## Main Contents

- Stack abstraction:
  - `struct o2cb_stack_ops` defines list, join, complete-join, and leave operations.
  - Classic `o2cb` stack uses configfs heartbeat management.
  - Userspace stack uses `ocfs2_controld` protocol, with optional CMAP/FSDLM shortcuts.
- Stack detection/setup:
  - Reads `/sys/fs/ocfs2/cluster_stack`.
  - Falls back to setting up classic stack when missing.
  - `o2cb_setup_stack()` can modprobe `ocfs2`, `ocfs2_stack_user`, or `ocfs2_stack_o2cb`, then write desired stack label.
- Interface initialization:
  - `o2cb_init()` validates nodemanager interface revision from current and legacy sysfs/proc paths.
  - Detects configfs at `/sys/kernel/config` or legacy `/config` and verifies configfs magic.
- Configfs cluster/node operations:
  - `o2cb_create_cluster()` / `o2cb_remove_cluster()`.
  - `o2cb_add_node()` creates a node then writes `ipv4_port`, `ipv4_address`, `num`, and `local`.
  - `o2cb_del_node()` removes node directories.
  - Attribute read/write helpers translate errno into O2CB error table values.
- Heartbeat region operations:
  - Creates heartbeat region directories, writes block size/start/count, opens device, and passes device fd number to configfs `dev` attribute.
  - Removes heartbeat regions and maps busy/in-use errors.
  - Supports fake default cluster lookup when caller omits cluster name.
- SysV semaphore reference counting:
  - Region name CRC32 becomes semaphore key.
  - Two semaphores are used: one mutex and one reference count.
  - Handles races with removed semaphore sets and supports `SEM_UNDO` based on persistent/nonpersistent region usage.
- Classic join/leave:
  - Validates stack, cluster name, and disk heartbeat flags against running config.
  - Starts/stops local heartbeat for non-global heartbeat mode.
  - Global heartbeat is assumed already managed by cluster online/offline flow.
- Userspace stack join/leave:
  - Connects to `ocfs2_controld` and sends `MOUNT`, `MRESULT`, or `UNMOUNT`.
  - Parses daemon `STATUS` responses and maps daemon errors.
  - Can bypass controld when FSDLM recovery callback support is available for appropriate PCMK/libdlm versions.
- Cluster discovery/listing:
  - Lists classic clusters/nodes/heartbeat regions by reading configfs directories.
  - Lists userspace clusters via Corosync CMAP when available or daemon protocol otherwise.
  - `o2cb_running_cluster_desc()` builds current stack/cluster/flags descriptor.
- Heartbeat mode and debug:
  - Reads/writes configfs heartbeat `mode`.
  - `o2cb_control_daemon_debug()` requests daemon dump list and concatenates it.
  - `o2cb_get_hb_thread_pid()` reads heartbeat thread pid.
- Control device:
  - Opens `/dev/misc/ocfs2_control`.
  - Negotiates fixed protocol `T01\n`.
  - Sends node id and locking protocol version.
  - Sends `DOWN` messages for node-down notifications.
- Miscellaneous:
  - Reads max locking protocol from `/sys/fs/ocfs2/max_locking_protocol`.
  - Reads old heartbeat control path from `/proc/sys/fs/ocfs2/nm/hb_ctl_path`.

## Dependencies and Integration

- Depends on libo2cb public headers, `o2cb_client_proto`, configfs path macros from `o2cb_abi.h`, CRC32 helper, and libocfs2 memory/error definitions.
- Conditional integration with Corosync CMAP and libdlm/FSDLM.
- Used by higher-level OCFS2 tooling for cluster online/offline state, mount group joins, heartbeat management, and locking protocol negotiation.

## Research Notes

- Error handling consistently maps system errors to O2CB error-table values, but many fallback paths intentionally collapse unexpected states into internal failure or service unavailable.
- Configfs path formatting uses `PATH_MAX - 1` sentinel checks; most paths are rejected if formatting reaches that boundary.
- Heartbeat references are cross-process state, so semaphore cleanup and `SEM_UNDO` behavior are core correctness mechanisms.
- Userspace stack operations maintain global `control_daemon_fd`, so only one join transaction can be in progress in a process.
