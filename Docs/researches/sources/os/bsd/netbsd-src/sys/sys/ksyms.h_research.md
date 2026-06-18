# File Research: sources/os/bsd/netbsd-src/sys/sys/ksyms.h

Defines kernel symbol table interfaces and ioctls. Private mode exposes active symbol table descriptors, ELF export header construction, CTF attachment fields, and pslist integration. Public structures support old and current symbol/value lookup ioctls. Kernel APIs provide name/value lookup, module symbol iteration, add/delete symbol tables, initialization, ELF symbol ingestion, availability, and module load/unload notifications.

This integrates debugging, module loading, DDB, and `/dev/ksyms`. Risks include ELF-size compatibility, user ABI differences between old/new symbol ioctls, symbol table lifetime while open, and safe exposure of kernel addresses.
