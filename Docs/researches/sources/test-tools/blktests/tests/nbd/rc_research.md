<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/rc -->
# sources/test-tools/blktests/tests/nbd/rc

Purpose: shared `tests/nbd/rc` support for Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. It defines 11 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`; functions `group_requires()` lines 9-11, `_have_nbd()` lines 13-28, `_have_nbd_netlink()` lines 30-42, `_wait_for_nbd_connect()` lines 44-53, `_wait_for_nbd_disconnect()` lines 55-63, `_start_nbd_server()` lines 65-84, `_stop_nbd_server()` lines 86-90, `_start_nbd_server_netlink()` lines 92-95, `_stop_nbd_server_netlink()` lines 97-100, `_netlink_connect()` lines 102-104, `_netlink_disconnect()` lines 106-108; external commands `nbd-client`, `grep`, `sleep`, `cat`.

Control flow: `group_requires()` uses local helpers `_have_nbd`; gates `_have_root`, `_have_nbd`.

State and persistence behavior: touches state paths such as `/sys/kernel/debug/nbd/nbd0/tasks`, `/dev/nbd0`, `/dev/null`, `$FULL`, `$(lsblk --raw --noheadings -o SIZE /dev/nbd0)`, `$(cat "${TMPDIR}/nbd.pid")` writes diagnostic command output to the blktests `$FULL` log records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `common/rc`; requirement gates include `_have_root`, `_have_nbd`, `_have_driver nbd`, `_have_program nbd-server`, `_have_program nbd-client`, `_have_nbd_netlink`, `_have_program genl-ctrl-list`; runtime command surface includes `nbd-client`, `grep`, `sleep`, `cat`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/rc -->
