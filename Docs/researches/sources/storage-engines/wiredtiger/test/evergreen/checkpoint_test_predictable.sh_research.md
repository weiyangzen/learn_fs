<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/checkpoint_test_predictable.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/checkpoint_test_predictable.sh

Purpose: verifies deterministic checkpoint behavior by replaying `test_checkpoint` with predictable mode and timestamps. It must run from the `cmake_build/test/checkpoint` directory and accepts an iteration count followed by arbitrary checkpoint arguments.

Important behavior: `rando()` derives decimal seeds from `/dev/urandom`. A calibration run creates `RUNDIR_0` with fixed data seed and extra seed, runs predictable/timestamp mode (`-x -R` plus `-PSD...`), then reads the stable timestamp using `tools/wt_timestamps`. Each later iteration runs two homes (`RUNDIR_1`, `RUNDIR_2`) to the same stop timestamp and same data seed but different extra seeds, then compares directories with `tools/wt_cmp_dir`.

State and persistence: repeatedly removes and recreates `RUNDIR_0/1/2`; persistent evidence is stdout plus any retained failing directories. It uses no global state except the generated seeds and timestamp.

Dependencies and integration: depends on `test_checkpoint`, `tools/wt_timestamps`, and `tools/wt_cmp_dir`. It is wired into Evergreen checkpoint predictable tasks.

Risks and test signals: failures come from calibration/test binary exit status or directory mismatch. Seed generation strips leading zeroes, but empty output from the pipeline would produce malformed seeds. The cwd guard prevents accidental execution from the wrong build location.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/checkpoint_test_predictable.sh -->
