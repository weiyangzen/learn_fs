<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/qemu_multiarch_testing/hdc.dir/init2 -->
# sources/test-tools/strace/attic/qemu_multiarch_testing/hdc.dir/init2

Purpose: second-stage QEMU image script that configures, builds, tests, and optionally uploads strace from inside the emulated system.

Important commands: unmounts `/mnt`, then in a traced subshell runs `cd strace`, `./configure`, `make`, `size strace`, `make check VERBOSE=1` with test-suite log printing, and optional `ftpput` controlled by `FTP_PORT`/`FTP_SERVER`. Output is piped through `tee strace_build.log`; then `/home` is remounted read-only, synced, and delayed.

Control flow: `set -e -x` applies inside the subshell, but `make check && cat ... || :` prevents test failures from aborting that compound command.

State and persistence: writes build tree outputs and `strace_build.log`; optionally uploads the `strace` binary.

Dependencies and integration: assumes shell utilities, compiler toolchain, mount support, and optional BusyBox-style `ftpput`.

Risks: test failures can be masked by `|| :`. Credentials/server settings are environment-driven. Read-only remount can fail silently because the script lacks `set -e` globally. Test signals: inspect `strace_build.log`, `tests/test-suite.log`, and uploaded binary presence when FTP variables are set.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/qemu_multiarch_testing/hdc.dir/init2 -->
