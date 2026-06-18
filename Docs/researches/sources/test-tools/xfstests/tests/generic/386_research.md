# sources/test-tools/xfstests/tests/generic/386

## Purpose
This test checks the project quota values reported by the quota "df" and "report" subcommands to ensure they match what they should be. There was a bug (fixed by xfsprogs commit 7cb2d41b) where the values reported were double what they should have been. SGI PV 1015651. It is registered as generic/386 with `_begin_fstest` tags `auto, quick, quota`, making it part of the quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _filter_quota_rpt, _quota_cmd. Important state variables and paths include my_projects=$tmp.projects, my_projid=$tmp.projid, proj_name=test_project, proj_num=1, qlimit_meg=500, proj_dir=$SCRATCH_MNT/test. Topic focus: quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; wraps repeated scenarios in local helper functions _filter_quota_rpt, _quota_cmd.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_quota; _require_xfs_quota_foreign; _require_scratch; _require_prjquota $SCRATCH_DEV.

External/helper commands: awk, df, mkdir, rm.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
