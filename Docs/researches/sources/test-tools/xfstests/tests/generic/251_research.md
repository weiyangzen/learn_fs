# sources/test-tools/xfstests/tests/generic/251

## Purpose

This test was created in order to verify filesystem FITRIM implementation By many concurrent copy and remove operations and checking that files does not change after copied into SCRATCH_MNT test if FITRIM implementation corrupts the filesystem (data/metadata). It is registered with `_begin_fstest ioctl trim auto` and is part of the xfstests generic suite, so the same script is intended to validate the behavior across every filesystem that satisfies its feature gates.

## Important APIs, Types, and Functions

This is an executable xfstests bash test. Its runner-facing interface is the numbered script `251` plus `_begin_fstest ioctl trim auto`. Imported libraries: `. ./common/preamble`, `. ./common/filter`. Capability gates: `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. Local functions: `_cleanup`, `_destroy`, `_destroy_fstrim`, `_fail`, `set_minlen_constraints`, `set_length_constraints`, `fstrim_loop`. The important external command surface is the xfstests harness variables (`$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, `$seqres.full`) plus helper programs invoked from `$here/src` and command variables such as `$XFS_IO_PROG` or `$FIO_PROG` when present.

Notable variables and setup values:

- Line 15: `tmp=`mktemp -d``
- Line 18: `mypid=$$`
- Line 106: `fsize=$(_discard_max_offset_kb "$SCRATCH_MNT" "$SCRATCH_DEV")`
- Line 110: `step=$((RANDOM*$RANDOM+4))`
- Line 114: `minlen=$(( (RANDOM * (RANDOM % 2 + 1)) % FSTRIM_MAX_MINLEN ))`
- Line 118: `start=$RANDOM`
- Line 121: `fpid=$!`
- Line 127: `fpid=$!`

## Control Flow

The visible phases are driven by echo markers such as line 50 `echo "$1"`, line 178 `echo "MINLEN max=$FSTRIM_MAX_MINLEN min=$FSTRIM_MIN_MINLEN" >> $seqres.full`, line 179 `echo "LENGTH max=$FSTRIM_MAX_LEN min=$FSTRIM_MIN_LEN" >> $seqres.full`, line 193 `echo -n "Running the test: "`. Reusable shell functions encapsulate repeated setup or validation before the main body invokes them in sequence. After setup, the test prepares files or devices, performs the filesystem operation under test, and validates through filtered command output or explicit assertions.

Key operational lines:

- Line 23: `_require_scratch`
- Line 24: `_scratch_mkfs >/dev/null 2>&1`
- Line 25: `_scratch_mount`
- Line 31: `rm -rf $tmp`
- Line 36: `kill $pids $fstrim_pid 2> /dev/null`
- Line 38: `rm -rf $tmp`
- Line 43: `test -n "$fpid" && kill $fpid 2> /dev/null`
- Line 45: `rm -f $tmp.fstrim_loop`
- Line 51: `kill $mypid 2> /dev/null`
- Line 133: `rm -f $tmp.fstrim_loop`
- Line 139: `find -P . -xdev -type f -print0 | xargs -0 md5sum | sort -o $tmp/stress.$$.$p`
- Line 146: `rm -f $tmp/stress.$$.$p`
- Line 162: `rm -rf $SCRATCH_MNT/$p`
- Line 205: `test -e "$tmp.fstrim_loop" && truncate -s 0 $tmp.fstrim_loop`

## State and Persistence Behavior

Primary state is created under `$SCRATCH_MNT` on a freshly formatted scratch filesystem, so the test can destroy, remount, or cycle the filesystem without touching the configured test directory. Temporary files are rooted at `$tmp.*` and removed by the local or default cleanup path. The only durable outputs expected outside the exercised filesystem are normal xfstests artifacts such as `$seqres.full`; local cleanup removes `$tmp.*` and test files when the script overrides `_cleanup`.

## Dependencies and Integration Points

It integrates with the xfstests runner through `_begin_fstest` tags `ioctl`, `trim`, `auto`, imports `. ./common/preamble`, `. ./common/filter`, and uses capability gates such as `_require_scratch`, `_require_batched_discard $SCRATCH_MNT`. The script reports detailed command output to `$seqres.full` where needed and relies on the numbered golden output for user-visible pass/fail text. It also depends on the common xfstests semantics for `_notrun`, `_fail`, filtered output, scratch formatting, user/group identities, and external helper binaries referenced in the operation list.

## Risks and Edge Cases

- Direct I/O paths can be affected by device sector size, alignment, cache invalidation, and filesystem-specific serialization between buffered and direct writes.
- Thin-provisioning tests depend on device-mapper target behavior, pool exhaustion semantics, and correct cleanup of temporary block devices.
- Stress tests are randomized or high-iteration workloads, so seeds, scaling helpers, timeouts, and captured stderr are important for reproducibility.
- Several checks can intentionally call `_notrun`; this is expected for unsupported geometry or feature combinations and should be distinguished from a failing assertion.

## Test Signals

The pass signal is filtered `md5sum` output, stress-tool exit status and captured logs, explicit `_fail` assertions. Regressions show up as golden-output mismatches, unexpected stderr in `$seqres.full`, skipped capability gates, failed helper status, or nonzero final `status`.
