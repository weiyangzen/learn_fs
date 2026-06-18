# sources/test-tools/xfstests-bld/run-fstests/android-xfstests

Purpose: Android runner for xfstests. It boots an optional kernel through fastboot, deploys an xfstests chroot/rootfs onto a rooted Android device, prepares partitions, runs tests or interactive shell commands, and captures logs.

Important functions: `die`, `ask_yesno`, `adb_ready`, `fastboot_ready`, `wait_for_device`, `reboot_into_fastboot_mode`, `query_kernel_version`, `extract_kernel_version`, `boot_kernel`, `chroot_prepare`, `chroot_wipe`, `chroot_run`, `chroot_interactive_shell`, `setup_chroot`, `try_shrink_userdata`, `setup_partitions`, `xfstests_running`, and `stop_existing_tests`.

Control flow: handles `install-kconfig`/`kbuild` passthrough commands, sources config and CLI parsing, sets log file, verifies adb/fastboot, stops existing tests unless shell-like command, loops through kernel boot, chroot deployment, and partition setup, optionally reformats userdata smaller, then either enters shell or pushes a generated `/run-xfstests` script and runs it through chroot with tee logging.

State/persistence: modifies the attached device: `/data/xfstests-chroot`, `/data/xfstests-results`, bind mounts, loop device nodes, chroot md5 marker, test partitions, and potentially userdata formatting. Host logs persist under `$DIR/logs` unless `SKIP_LOG`.

Dependencies/integration: depends on adb, fastboot, root adbd, permissive SELinux, rootfs tarball, android test appliance scripts, shared util config/CLI/arch functions, and optional kernel image.

Risks: destructive path can reformat userdata after confirmation. Root shell commands interpolate variables into adb shell heredocs, so paths must be trusted. Kernel-version extraction by grepping image banners is heuristic. Device state/mount cleanup failures can affect later runs.

Test signals: successful chroot md5 reuse, partition setup result files, kernel version verification, log output, and xfstests result summaries validate behavior; manual device tests are required.
