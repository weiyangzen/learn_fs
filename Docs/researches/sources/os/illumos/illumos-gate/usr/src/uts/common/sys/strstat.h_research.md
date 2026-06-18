# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strstat.h

`strstat.h` defines the historical per-module STREAMS statistics structure `module_stat`. Counters track calls to put, service, open, close, and admin procedures (`ms_pcnt`, `ms_scnt`, `ms_ocnt`, `ms_ccnt`, `ms_acnt`). The structure also provides a private statistics buffer pointer and size (`ms_xptr`, `ms_xsize`).

`stream.h` references `struct module_stat *qi_mstat` from `struct qinit`, making this header part of the module publication ABI even though the contents are small.
