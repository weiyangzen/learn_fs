# File Research: sources/teaching/minix/minix/fs/procfs/glo.h

`glo.h` declares cross-module ProcFS globals: `pid_files[]` from `pid.c`, `root_files[]` from `root.c`, and `proc_list[NR_PROCS]` from `tree.c`.

These declarations connect the static tree builder, dynamic PID tree manager, and PID-file generator registry without introducing a separate global-definition pattern like MFS uses.
