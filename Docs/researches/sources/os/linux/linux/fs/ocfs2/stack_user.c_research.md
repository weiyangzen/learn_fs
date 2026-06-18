# File Research: sources/os/linux/linux/fs/ocfs2/stack_user.c

## Purpose

`stack_user.c` implements the OCFS2 cluster stack plugin named `user`, which connects OCFS2 to Linux `fs/dlm` and, for older userspace-controlled stacks, to `/dev/ocfs2_control`. It bridges OCFS2's generic cluster stack operations from `stackglue.h` to `dlm_lockspace_t`, `dlm_lock()`, `dlm_unlock()`, and DLM POSIX lock helpers.

## Major Components

- `/dev/ocfs2_control` miscdevice protocol:
  - Performs a text handshake using protocol tag `T01\n`.
  - Requires a `SETN <8-hex-node>\n` node-number message.
  - Requires a `SETV <2-hex-major> <2-hex-minor>\n` locking protocol version message.
  - Accepts `DOWN <32-hex-uuid> <8-hex-node>\n` recovery notifications once the handshake is valid.
- `struct ocfs2_live_connection`:
  - Tracks a mounted filesystem's cluster connection, connection type, local node id, slot, DLM version lock state, LVB, completion, and waitqueue.
  - Is shared between mount-side cluster connection state and miscdevice-side recovery notifications.
- `struct ocfs2_control_private`:
  - Per-open miscdevice state for handshake progress, proposed node id, and proposed protocol version.
- `ocfs2_user_plugin`:
  - Registers stack operations for connect, disconnect, local node lookup, DLM lock/unlock/status/LVB helpers, POSIX plocks, and debug dumping.

## Control Protocol Behavior

The control device is stateful per file descriptor:

- Initial state rejects writes until userspace reads the whole protocol list.
- `ocfs2_control_read()` returns the supported protocol tag and advances to `OCFS2_CONTROL_HANDSHAKE_READ` after EOF of that tag.
- The next write must match `OCFS2_CONTROL_PROTO`.
- Configuration messages are accepted in `OCFS2_CONTROL_HANDSHAKE_PROTOCOL`.
- Valid runtime `DOWN` messages require `OCFS2_CONTROL_HANDSHAKE_VALID`.

Global control state is protected by `ocfs2_control_lock`:

- `ocfs2_control_this_node` is global for the active control daemon.
- `running_proto` is the selected filesystem locking protocol.
- `ocfs2_control_opened` counts valid control daemon opens.
- `ocfs2_live_connection_list` allows `DOWN` messages to find a mounted filesystem by UUID/name and call its recovery handler.

If the last valid control fd is released while live controlled connections remain, the code logs a severe error and calls `emergency_restart()`. This is intentional fail-fast behavior because cluster recovery notifications are no longer reliable.

## DLM Integration

The file wraps `fs/dlm` APIs in OCFS2 stack operations:

- `user_dlm_lock()` ensures an LVB pointer exists inside the `ocfs2_dlm_lksb` storage and calls `dlm_lock()` with `DLM_LKF_NODLCKWT`.
- `user_dlm_unlock()` calls `dlm_unlock()` with the `fs/dlm` lock id.
- `fsdlm_lock_ast_wrapper()` maps `-DLM_EUNLOCK` and `-DLM_ECANCEL` statuses to OCFS2 unlock ASTs; other statuses call the OCFS2 lock AST.
- `fsdlm_blocking_ast_wrapper()` forwards blocking ASTs to the OCFS2 locking protocol.
- `user_plock()` demultiplexes POSIX lock operations to `dlm_posix_cancel()`, `dlm_posix_get()`, `dlm_posix_unlock()`, or `dlm_posix_lock()`.

## Locking Protocol Negotiation

For modern `NO_CONTROLD` mode, protocol negotiation uses the LVB of a special DLM lock named `version_lock`:

- First mount takes `version_lock` in EX mode with `NOQUEUE`, writes the local max protocol to the LVB, then converts to PR mode.
- Later mounts take PR mode and read the LVB.
- A major-version mismatch or peer minor version greater than local max fails the mount.
- `fs_protocol_compare()` enforces that major versions match and clamps the connection minor version down to the already-running minor if needed.

For `WITH_CONTROLD` mode, userspace must provide node id and locking version through `/dev/ocfs2_control`; `ocfs2_control_install_private()` only publishes global state after both are available and compatible with active mounts.

## Mount/Recovery Flow

`user_cluster_connect()`:

- Allocates `ocfs2_live_connection`, initializes wait/completion state, and creates a DLM lockspace with `dlm_new_lockspace()`.
- Detects older dlm_controld behavior via `ops_rv == -EOPNOTSUPP` and switches to `WITH_CONTROLD`.
- Attaches the live connection to the control list.
- In `NO_CONTROLD` mode, negotiates protocol through `version_lock` and waits until `recover_done` supplies a positive node id.
- Verifies the connection protocol against `running_proto`.

DLM lockspace callbacks:

- `user_recover_slot()` logs node-down events and invokes OCFS2 recovery.
- `user_recover_done()` records the local node id and slot, then wakes the mount path.
- `user_recover_prep()` is intentionally empty.

`user_cluster_disconnect()` releases the version lock, releases the lockspace, drops the live connection, and clears connection private state.

## Dependencies

- Uses `stackglue.h` types and registration functions.
- Uses Linux `fs/dlm` and `dlm_plock` APIs.
- Calls OCFS2 recovery through `cc_recovery_handler`.
- Exposes a loadable module with `module_init()`/`module_exit()` that registers/unregisters the `user` stack plugin.

## Correctness Notes

- The control protocol deliberately requires exact write sizes so one write maps to one command.
- `ocfs2_control_lock` serializes global handshake state, live connection list changes, and control release behavior.
- The code assumes `ocfs2_live_connection_attach()` is called from the VFS mount path, where duplicate `fill_super()` calls for the same mount are prevented.
- The LVB protocol version fields are two `u8` values, so no endian conversion is required.
- In `user_cluster_connect()`, the error path has to avoid double-freeing `lc` after `user_cluster_disconnect()` has already dropped it; the code sets `lc = NULL` before the final cleanup path.
