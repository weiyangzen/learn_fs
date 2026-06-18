<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/rc -->
# sources/test-tools/blktests/tests/rnbd/rc

Purpose: shared `tests/rnbd/rc` support for RNBD client/server smoke and stress coverage for remote block-device mapping over loopback RDMA. It defines 4 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/multipath-over-rdma`; functions `_have_rnbd()` lines 10-17, `_setup_rnbd()` lines 19-29, `_stop_rnbd_client()` lines 36-44, `_start_rnbd_client()` lines 46-52; external commands `grep`, `echo`.

Control flow: `_have_rnbd()` uses gates `_have_driver rdma_rxe`, `_have_driver rnbd_server`, `_have_driver rnbd_client`.

State and persistence behavior: touches state paths such as `/sys/block/rnbd`, `/sys/devices/virtual/rnbd-client/ctl/map_device`, `/dev/null`, `$(rdma_network_interfaces)`, `$(get_ipv4_addr "$i")`, `$(ls -d /sys/block/rnbd* 2>/dev/null)` records skip reasons in the shared harness array instead of failing unsupported hosts.

Dependencies and integration points: integrates with the blktests `rnbd` suite and the shared harness; through `common/rc`, `common/multipath-over-rdma`; requirement gates include `_have_rnbd`, `_have_driver rdma_rxe`, `_have_driver rnbd_server`, `_have_driver rnbd_client`; runtime command surface includes `grep`, `echo`.

Risks and test signals: contains loops or background/concurrent work, making cleanup and race timing important test signal is largely shell return status plus explicit comparisons in the `$FULL` log unsupported prerequisites should skip cleanly through `SKIP_REASONS`.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/rnbd/rc -->
