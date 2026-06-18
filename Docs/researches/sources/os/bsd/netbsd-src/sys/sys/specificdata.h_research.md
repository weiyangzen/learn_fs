# File Research: sources/os/bsd/netbsd-src/sys/sys/specificdata.h

Read completely: 69 lines.

This header declares a generic kernel specific-data facility. It defines key, destructor, domain, container, and reference types; `specificdata_reference` stores a container pointer and lock.

APIs cover domain create/delete, key create/delete with destructor, per-object init/fini, locked and unlocked getspecific, setspecific, and nonblocking setspecific.

Risks: object lifetime must coordinate domain/key deletion, per-object finalization, destructors, and reference locking. The unlocked getter requires external synchronization.
