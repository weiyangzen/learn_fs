<!-- BEGIN_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/004 -->
# sources/test-tools/blktests/tests/nbd/004

Purpose: Network Block Device coverage that exercises module loading, exported file-backed devices, partition handling, resize, disconnect, mount, and concurrent socket clearing. This specific test is declared as: "module load/unload concurrently with connect/disconnect".

Important APIs/types/functions: sourced libraries `tests/nbd/rc`; top-level variables `DESCRIPTION=module load/unload concurrently with connect/disconnect`, `QUICK=1`; functions `requires()` lines 13-15, `module_load_and_unload()` lines 17-22, `connect_and_disconnect()` lines 24-29, `test()` lines 31-71; external commands `modprobe`, `echo`, `sleep`, `grep`, `nbd-client`.

Control flow: `requires()` uses gates `_have_module nbd`. `test()` uses local helpers `module_load_and_unload`, `connect_and_disconnect`; commands `echo`, `sleep`, `grep`, `nbd-client`.

State and persistence behavior: touches state paths such as `/dev/null`, `$((i + 1)` loads or unloads kernel modules, so host module parameters and device lifetimes are part of the test state.

Dependencies and integration points: integrates with the blktests `nbd` suite and the shared harness; through `tests/nbd/rc`; requirement gates include `_have_module nbd`; runtime command surface includes `modprobe`, `echo`, `sleep`, `grep`, `nbd-client`.

Risks and test signals: marked `QUICK=1`, so it is intended for fast smoke coverage but still depends on host capability gates contains loops or background/concurrent work, making cleanup and race timing important exercises privileged kernel/device-management paths that can leave host state behind if interrupted test signal is largely shell return status plus explicit comparisons in the `$FULL` log.
<!-- END_FILE_RESEARCH: sources/test-tools/blktests/tests/nbd/004 -->
