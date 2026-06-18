<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/schema_abort_predictable.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/schema_abort_predictable.sh

Purpose: validates predictable replay for `test_schema_abort`, where concurrent schema operations are replayed to a calibrated operation count and compared.

Control flow: must run from `build/test/csuite/schema_abort`, accepts `times`, sets runtime 20 seconds and 5 threads, performs a calibration run into `RUNDIR_0`, reads stable timestamp from `RUNDIR_0/WT_HOME`, and treats that as operation count. For each iteration it runs two predictable homes with the same data seed, different extra seeds, and a slightly randomized operation limit, then compares `WT_HOME` directories with `wt_cmp_dir`, ignoring `table:wt`.

State and persistence: recreates `RUNDIR_0/1/2`; retains failing directories. Uses generated seeds and operation counts.

Dependencies and integration: Evergreen schema abort predictable task. Requires `test_schema_abort`, `tools/wt_timestamps`, and `tools/wt_cmp_dir`.

Risks and test signals: ignores `table:wt` because that table can be concurrently created/opened/verified/dropped and does not participate in predictable replay. The optional usage text mentions an unused second arg. Failures are binary exit or directory mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/schema_abort_predictable.sh -->
