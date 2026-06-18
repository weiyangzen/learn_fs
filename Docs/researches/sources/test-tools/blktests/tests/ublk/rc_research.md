<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/rc -->
# sources/test-tools/blktests/tests/ublk/rc

Purpose: shared `tests/ublk/rc` support for ublk userspace block-driver coverage for add/delete, mount, crash, recovery, and daemon-kill behavior. It defines 1 shell helpers that individual tests source for requirement gates, setup/cleanup, target/device construction, and result checking.

Important APIs/types/functions: sourced libraries `common/rc`, `common/ublk`; functions `group_requires()` lines 10-14; external commands `ublk`.

Control flow: `group_requires()` uses gates `_have_root`, `_have_ublk`, `_have_fio`.

State and persistence behavior: has no durable repository state; all observable state is temporary process, device, or build output handled by the caller.

Dependencies and integration points: integrates with the blktests `ublk` suite and the shared harness; through `common/rc`, `common/ublk`; requirement gates include `_have_root`, `_have_ublk`, `_have_fio`; runtime command surface includes `ublk`.

Risks and test signals: exercises privileged kernel/device-management paths that can leave host state behind if interrupted.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/ublk/rc -->
