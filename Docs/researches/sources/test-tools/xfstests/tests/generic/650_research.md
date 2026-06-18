# sources/test-tools/xfstests/tests/generic/650

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/650`. Run an all-writes fsstress run with multiple threads while exercising CPU hotplugging to shake out bugs in the write path. It is registered with `_begin_fstest auto rw stress soak`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 91 source line(s).
- Harness registration: `_begin_fstest auto rw stress soak`.
- Imported common libraries: `./common/preamble`.
- Capability and skip gates: `_fixed_by_fs_commit xfs ecd49f7a36fb "xfs: fix per-cpu CIL structure aggregation racing with dying cpus"`, `_require_test`.
- Local shell functions: `_cleanup`, `exercise_cpu_hotplug`.
- External `$here/src` helpers: none visible.
- Notable variables and constants:
- `sysfs_cpu_dir="/sys/devices/system/cpu"`
- `nrcpus=$(getconf _NPROCESSORS_CONF)`
- `hotplug_cpus=()`
- `nr_hotplug_cpus="${#hotplug_cpus[@]}"`
- `stress_dir="$TEST_DIR/$seq"`
- `sentinel_file=$tmp.hotplug`
- `fsstress_args=(-w -d $stress_dir)`
- `nr_cpus=$((LOAD_FACTOR * nr_hotplug_cpus))`
- `nr_ops=$((2500 * TIME_FACTOR))`

## Control Flow

- Capability gating runs first through `_fixed_by_fs_commit xfs ecd49f7a36fb "xfs: fix per-cpu CIL structure aggregation racing with dying cpus"`, `_require_test`.
- User-visible phase markers include:
- `line 22: echo 1 > "$i" 2>/dev/null`
- `line 36: echo "$action" > "$sysfs_cpu_dir/cpu$cpu/online" 2>/dev/null`
- `line 56: echo "Silence is golden."`
- Key operational lines include:
- `line 19: _kill_fsstress`
- `line 31: while [ -e $sentinel_file ]; do`
- `line 62: fsstress_args=(-w -d $stress_dir)`
- `line 68: fsstress_args+=(-p $nr_cpus)`
- `line 71: fsstress_args+=(--duration="$((SOAK_DURATION / 10))")`
- `line 74: fsstress_args+=(--duration=3)`
- `line 78: fsstress_args+=(-n $nr_ops)`
- `line 82: _run_fsstress "${fsstress_args[@]}"`

## State and Persistence Behavior

Uses the configured xfstests test area or an explicitly created loop/image mount rather than always reformatting the scratch device. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto rw stress soak`, common helper libraries (`./common/preamble`), and the golden-output file `sources/test-tools/xfstests/tests/generic/650.out` (2 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_fixed_by_fs_commit xfs ecd49f7a36fb "xfs: fix per-cpu CIL structure aggregation racing with dying cpus"`, `_require_test`.

## Risks and Edge Cases

- Most failures should surface as unexpected output, nonzero helper status, or harness `_fail`/`_notrun` behavior.

## Test Signals

The paired `.out` file has 2 line(s); its first visible signals are: 'QA output created by 650; Silence is golden.'. Runtime pass/fail is also signaled by hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
