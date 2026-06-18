# File Research: sources/os/bsd/freebsd-src/sys/sys/interrupt.h

Defines the machine-independent interrupt event and handler framework. `struct intr_handler` stores filter and threaded handler callbacks, argument, flags, name, priority, owning event, and chain link. Handler flags represent network handlers, exclusivity, entropy, dead/suspended state, changed state, and MPSAFE behavior.

`struct intr_event` represents an interrupt source with handler list, lock, source cookie, interrupt thread, MD hooks for pre/post ithread, post-filter, CPU assignment, flags, cumulative handler flags, storm warning state, irq number, CPU binding, and phase/active counters.

APIs create/destroy events, add/remove/suspend/resume/describe handlers, bind events/ithreads, handle interrupts, manage affinity, and create/schedule/remove software interrupts. It also declares global interrupt statistics tables.
