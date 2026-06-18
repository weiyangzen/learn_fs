## sources/test-tools/xfstests/common/ubifs

Purpose: this tiny UBIFS helper exposes the usable logical eraseblock size for a UBI volume.

Important API: `_get_leb_size ubivol` prints `/sys/class/ubi/<basename(ubivol)>/usable_eb_size`.

Control flow: it takes one argument, strips any directory prefix with `basename`, and cats the corresponding sysfs attribute.

State and persistence: no state is created or mutated. It reads kernel sysfs only.

Dependencies and integration: callers must pass a valid UBI volume path, typically `$SCRATCH_DEV` or `$TEST_DEV` for `FSTYP=ubifs`. It depends on sysfs UBI class layout and `cat`.

Risks: missing arguments or invalid devices produce a raw `cat` error rather than `_notrun` or `_fail`. The function assumes UBI volume basename matches the sysfs directory name.

Test signals: success is a numeric usable eraseblock size on stdout. Failure indicates an invalid UBI volume, missing sysfs, or insufficient kernel UBIFS/UBI support.
