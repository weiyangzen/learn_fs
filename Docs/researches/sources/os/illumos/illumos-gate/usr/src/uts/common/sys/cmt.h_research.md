# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmt.h

`cmt.h` defines chip multithreading processor-group support. It declares CMT scheduling policies (`NO_POLICY`, `BALANCE`, `COALESCE`, `AFFINITY`), CMT processor-group data, lgroup linkage, utilization macros, and capacity calculation.

Kernel functions update processor-group load, handle CPU startup, test migration feasibility, ask platform policy/ranking callbacks, balance threads, and enable/disable padding for hardware group types.
