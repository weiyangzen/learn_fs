<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/qemu_multiarch_testing/parallel-build-hdc-img.sh -->
# sources/test-tools/strace/attic/qemu_multiarch_testing/parallel-build-hdc-img.sh

Purpose: launches parallel native-build jobs for multiple QEMU system image directories using a common `hdc.img`.

Important functions: `build_in_dir(dir)` changes into a directory, removes `hdb.img`, runs `nice -n10 time ./native-build.sh ../hdc.img`, optionally deletes `hdb.img`, and writes a completion message to fd 3. Top-level logic scans command-line directories for `native-build.sh`, starts each in the background with logs redirected to `<dir>.log`, then waits.

Control flow: background fan-out, with `started` guarding empty input. `HDBMEGS=64` is exported and `keep_hdb=false` controls cleanup.

State and persistence: creates per-directory log files and transient or retained `hdb.img` files.

Dependencies and integration: assumes each system-image directory has `native-build.sh` compatible with the generated `hdc.img`.

Risks: no concurrency limit besides number of arguments. Failures are only visible in logs and aggregate `wait` does not identify which build failed. Test signals: check each `<dir>.log` and final "Finished" messages.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/qemu_multiarch_testing/parallel-build-hdc-img.sh -->
