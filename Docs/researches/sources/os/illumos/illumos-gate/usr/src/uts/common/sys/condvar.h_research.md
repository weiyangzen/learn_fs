# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/condvar.h

`condvar.h` defines the public kernel condition variable interface. `kcondvar_t` is an opaque 16-bit public representation, and `kcv_type_t` distinguishes default and driver condition variables.

Kernel builds define timeout resolution values for relative waits, validation macro `TIME_RES_VALID`, and prototypes for init/destroy, wait, stop-aware wait, timed waits, high-resolution timed waits, relative timed waits, signal-interruptible waits, swap/core variants, signal/broadcast, and absolute `waituntil` behavior.
