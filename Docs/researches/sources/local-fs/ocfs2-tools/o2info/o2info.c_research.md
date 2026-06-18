# File Research: sources/local-fs/ocfs2-tools/o2info/o2info.c

`o2info.c` is the CLI front end. It declares supported options as `struct o2info_option` entries, dynamically builds `getopt_long()` tables, appends selected operation objects to a task list, chooses the target path, opens it with the right method, and runs each requested operation.

It treats block/character devices as offline `libocfs2` targets and regular mounted objects as ioctl targets through `o2info_method()`. `-C/--cluster-coherent` flips the global `cluster_coherent` flag used by ioctl request flags.

Signal handling exits cleanly on termination signals, aborts on repeated SIGSEGV/SIGQUIT behavior, and ignores SIGPIPE. Main initialization sets up error tables, verbosity argv state, unbuffered output, and signals.

Risk notes: operation return values from `to_run()` are not accumulated in `o2info_run_task()`, duplicate long-only options report with the numeric generated value, and parsing errors often exit directly via `print_usage()`.
