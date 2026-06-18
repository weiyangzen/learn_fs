# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_bootstrap.c

Read completely: 153 lines.

Defines the temporary bootstrap disc strategy used before the full UDF strategy is selected. It only supports queueing read buffers directly to the device vnode strategy.

All logical-volume descriptor create/free/read/write operations panic because bootstrap mode is not supposed to perform node descriptor I/O or writing. Cache sync and init/finish hooks are no-ops.

The strategy table `udf_strat_bootstrap` is therefore a minimal read-only pass-through for early mount-time probing. Risk is misuse: any write or descriptor operation while this strategy is active is treated as a kernel programming error and panics.
