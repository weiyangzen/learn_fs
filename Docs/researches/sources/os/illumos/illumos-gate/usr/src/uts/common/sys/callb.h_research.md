# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/callb.h

`callb.h` defines callback classes and support for checkpoint/resume, panic, halt, uadmin, debugger entry, CPU deep idle, and related system events. Callback classes are numbered through `NCBCLASS`.

It defines `callb_cpr_t`, CPR state flags, timing/retry constants, and macros for initializing CPR state, marking safe/unsafe regions, and exiting. Kernel exports include callback registration/removal/execution, class execution, generic CPR handlers, stopped-thread checking, and callback table locking.
