# sources/sync-backup/casync/src/75-casync.rules.in

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/75-casync.rules.in -->
## sources/sync-backup/casync/src/75-casync.rules.in

Purpose: this is a udev rules template for casync's NBD integration. It asks udev to query `casync udev` for block devices matching `nbd*` and creates a symlink from the returned `CASYNC_NAME` environment value.

Important rules: removal events jump to `casync_end`. For block subsystem devices with kernel name `nbd*`, udev imports properties from `@bindir_unquoted@/casync udev %N`. If `ENV{CASYNC_NAME}` is non-empty, it appends a symlink using that name. The final label terminates the rule sequence.

Control flow: Meson configures `@bindir_unquoted@` into the generated `75-casync.rules`. At runtime, udev evaluates rules on device events. The import program runs only for matching NBD block devices that are not remove events.

State and persistence: installed state is the generated rule under the udev rules directory. Runtime state is udev-created device symlinks based on `CASYNC_NAME`.

Dependencies and integration points: integrates with `meson.build`, the `udev` option, libudev support, NBD block devices, and the `casync udev` command implementation elsewhere in `src`.

Risks: udev imports execute a casync binary on device events, so the path must be correct and the command must be fast and robust. Unsanitized or unexpected `CASYNC_NAME` values could affect symlink creation. Rules install only when `udev=true`.

Test signals: after installation, NBD device events should call `casync udev %N` and create symlinks only when a valid `CASYNC_NAME` is produced. Meson should configure the binary path correctly.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/75-casync.rules.in -->
