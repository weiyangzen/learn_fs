# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/job.c

Constructs and dumps `Job` records.

Key functions:
- `newjob()` allocates a job, stores the rule, target node list, stem, regex matches, prerequisite lists, target lists, and initializes `nproc = -1`.
- `dumpj()` prints one or all jobs for debugging, including target, alltarget, prereq, and new prereq lists.

Role:
- Jobs are produced by `recipe.c` and consumed by `run.c`.
