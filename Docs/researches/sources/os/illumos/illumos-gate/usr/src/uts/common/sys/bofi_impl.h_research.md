# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bofi_impl.h

`bofi_impl.h` contains private in-kernel BOFI state. `bofi_errent` stores linked error definitions, live error state, log base, state flags, condition variable, and soft interrupt id. State flags include active device, new message, waiter, and debug.

`bofi_shadow` records saved bus/access/DMA/interrupt operations, hash/list links, matching error-definition links, handle type, original handles, device identity, mapped ranges, pages, flags, and user-memory cookie. Handle type constants distinguish access, DMA, interrupt, and null handles.
