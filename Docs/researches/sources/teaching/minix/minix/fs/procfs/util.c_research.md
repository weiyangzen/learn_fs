# File Research: sources/teaching/minix/minix/fs/procfs/util.c

`util.c` implements `procfs_getloadavg`, a MINIX-specific load-average helper. It fetches kernel load history with `sys_getloadinfo`, caps requested output to three averages, and computes 1, 5, and 15 minute load averages from circular history slots.

The function accounts for the newest slot being partially filled by subtracting unfilled ticks from the denominator. It fills each `struct load` with total process-load ticks and the corresponding tick denominator, leaving formatting to `root_loadavg`.
