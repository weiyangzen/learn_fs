# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/dns64/dns64.h

Header for the Unbound DNS64 module.

Exports:
- `dns64_get_funcblock()`
- `dns64_init()`
- `dns64_deinit()`
- `dns64_operate()`
- `dns64_inform_super()`
- `dns64_clear()`
- `dns64_get_mem()`

Role in group:
- Module API contract that lets Unbound’s module framework instantiate and drive DNS64 processing.
