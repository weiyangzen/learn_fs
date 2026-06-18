# sources/test-tools/xfstests/tests/generic/621

## Purpose

This executable xfstests bash test researches `sources/test-tools/xfstests/tests/generic/621`. Test for a race condition where a duplicate filename could be created in an encrypted directory while the directory's encryption key was being added concurrently. This is a regression test for the following kernel commits: 968dd6d0c6d6 ("fscrypt: fix race allowing rename() and link() of ciphertext dentries") 75d18cd1868c ("ext4: prevent creating duplicate encrypted filenames") bfc2b7e85189 ("f2fs: prevent creating duplicate encrypted filenames") 76786a0f0834 ("ubifs: prevent creating duplicate encrypted filenames") The first commit fixed the bug for the rename() and link() syscalls. The others fixed the bug for the other syscalls that create new filenames. Note, the bug wasn't actually reproducible on f2fs.... It is registered with `_begin_fstest auto quick encrypt`, so the harness schedules it for filesystems satisfying the script gates and compares its visible output with the numbered `.out` golden file.

## Important APIs, Types, and Functions

- Script type: executable xfstests bash test with 157 source line(s).
- Harness registration: `_begin_fstest auto quick encrypt`.
- Imported common libraries: `./common/preamble`, `./common/filter`, `./common/encrypt`, `./common/renameat2`.
- Capability and skip gates: `_require_scratch_encryption -v 2`, `_require_renameat2 noreplace`.
- Local shell functions: `_cleanup`.
- External `$here/src` helpers: `if $here/src/renameat2 -n $dir/50 $dir/100 &> /dev/null; then`.
- Notable variables and constants:
- `runtime=$((5 * TIME_FACTOR))`
- `dir=$SCRATCH_MNT/dir`
- `inode=$(stat -c %i $dir/100)`
- `new_inode=$(stat -c %i $dir/100)`

## Control Flow

- Capability gating runs first through `_require_scratch_encryption -v 2`, `_require_renameat2 noreplace`.
- The test formats or constructs the filesystem/device image before exercising the behavior.
- It mounts the target filesystem, creates files/directories/metadata, and drives the regression scenario.
- It forces a remount, shutdown, unmount, or injected I/O failure when the assertion depends on persistence, recovery, or cache invalidation.
- It validates by comparing metadata/data, checking filesystem consistency, probing allocation maps, or emitting filtered golden output.
- User-visible phase markers include:
- `line 62: echo -e "\n# Creating encrypted directory containing files"`
- `line 79: echo -e "\n# Starting duplicate filename creator process"`
- `line 105: echo -e "\n# Starting add/remove enckey process"`
- `line 115: echo -e "\n# Running for a few seconds..."`
- `line 117: echo -e "\n# Stopping subprocesses"`
- `line 126: echo -e "\n# Checking for duplicate filenames via readdir"`
- `line 129: echo -e "\n# Checking for unexpected change in inode number"`
- `line 132: echo "Dentry changed inode number $inode => $new_inode!"`
- Key operational lines include:
- `line 53: _require_scratch_encryption -v 2`
- `line 54: _require_renameat2 noreplace`
- `line 56: _scratch_mkfs_encrypted &>> $seqres.full`
- `line 57: _scratch_mount`
- `line 64: _add_enckey $SCRATCH_MNT "$TEST_RAW_KEY"`
- `line 65: _set_encpolicy $dir $TEST_KEY_IDENTIFIER`
- `line 71: inode=$(stat -c %i $dir/100)`
- `line 86: while [ ! -e $tmp.done ]; do`
- `line 99: if $here/src/renameat2 -n $dir/50 $dir/100 &> /dev/null; then`
- `line 109: while [ ! -e $tmp.done ]; do`
- `line 110: _add_enckey $SCRATCH_MNT "$TEST_RAW_KEY" > /dev/null`
- `line 111: _rm_enckey $SCRATCH_MNT $TEST_KEY_IDENTIFIER > /dev/null`
- `line 121: _add_enckey $SCRATCH_MNT "$TEST_RAW_KEY" > /dev/null`
- `line 130: new_inode=$(stat -c %i $dir/100)`
- `line 145: echo -e "\n# Checking for duplicate filenames via fsck"`
- `line 146: _scratch_unmount`

## State and Persistence Behavior

Uses a freshly formatted scratch filesystem for destructive setup, so state is isolated under `$SCRATCH_MNT` and `$SCRATCH_DEV`. Mount transitions are part of the assertion surface; remount, unmount, or shutdown is used to force persistence, recovery, or cache invalidation. Encryption policy/key state is created during the test and used to check no-key/key-present transitions. A local `_cleanup` override tears down temporary files, mounts, background jobs, or synthetic devices.

## Dependencies and Integration Points

This file integrates with the xfstests runner through `_begin_fstest auto quick encrypt`, common helper libraries (`./common/preamble`, `./common/filter`, `./common/encrypt`, `./common/renameat2`), and the golden-output file `sources/test-tools/xfstests/tests/generic/621.out` (21 line(s)). It relies on standard xfstests environment variables such as `$TEST_DIR`, `$SCRATCH_MNT`, `$SCRATCH_DEV`, `$seq`, `$tmp`, and `$seqres.full`. Requirements and exclusions define the supported filesystem matrix: `_require_scratch_encryption -v 2`, `_require_renameat2 noreplace`.

## Risks and Edge Cases

- Feature gates depend on kernel, userspace tool, and filesystem support; unsupported features correctly produce `_notrun`.
- Directory mutation and rename races depend on dentry-cache timing and may need repeated attempts to expose regressions.

## Test Signals

The paired `.out` file has 21 line(s); its first visible signals are: 'QA output created by 621; # Creating encrypted directory containing files; Added encryption key with identifier 69b2f6edeee720cce0577937eb8a6751'. Runtime pass/fail is also signaled by explicit comparisons or filtered inspection commands, hang/race detection through background work, loops, or timeout windows. Regressions normally appear as unexpected stdout compared with `.out`, nonzero command status, `_fail` messages, fsck/check helper failures, or diagnostic detail appended to `$seqres.full`.
