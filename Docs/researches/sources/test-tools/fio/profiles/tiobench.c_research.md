# sources/test-tools/fio/profiles/tiobench.c

Purpose: implements a fio profile approximating tiotest/tiobench workloads.

Important APIs/functions: `tb_prep_cmdline()` fills dynamic option strings; static init/exit functions register/unregister `tiobench_profile`. Profile options include size, block size, number of runs, directory, and thread count.

Control flow: base `tb_opts` describes four jobs: sequential write, random write, sequential read, and random read, with stonewalls between phases, sync engine, direct IO, group reporting, threads, overwrite, and fixed filenames. `tb_prep_cmdline()` converts size from MiB to bytes or defaults to `4*1024*$mb_memory`, writes block size, loops, directory, and numjobs into static buffers, and returns the option list to the profile loader.

State and persistence: static option storage and static string buffers persist across runs. `dir` is marked `no_free`, so parser cleanup does not free it.

Dependencies and integration: profile framework, parser, option categories/groups, and fio job option ingestion.

Risks: static buffers assume formatted option values fit 80 bytes; directory paths longer than the buffer can overflow via `sprintf()`. Fixed filenames limit scaling beyond four files unless fio interprets them per job/thread as intended.

Test signals: generated command line for explicit/default size, long directories, different thread counts, and full profile execution in a scratch directory.
