# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_task.h

Defines libisns task ids, task payload union, and `struct isns_task_s`. The task structure stores task type, owning config, type-specific data, optional wait synchronization fields, wait reference count, and a `SIMPLEQ_ENTRY`.

It declares the dispatcher, end/wait routines, allocation/free helpers, queue insert/remove functions, and transaction-specific queue removal used by abort handling.
