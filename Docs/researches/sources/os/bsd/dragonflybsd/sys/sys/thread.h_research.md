# File Research: sources/os/bsd/dragonflybsd/sys/sys/thread.h

Architecture-independent LWKT thread, token, IPI, and CPU-sync definitions.

Key responsibilities:
- Defines LWKT pointer typedefs and run-queue type.
- Documents and defines LWKT tokens:
  - soft serialization
  - shared/exclusive modes
  - collision tracking
  - per-thread token reference stack
- Defines `struct lwkt_ipiq`, a per-CPU IPI FIFO with 256 slots.
- Defines `struct lwkt_cpusync`.
- Defines per-thread file descriptor cache structures.
- Defines the main `struct thread`, including:
  - queue links
  - message port
  - LWP/proc/PCB/globaldata associations
  - wait channel/domain/message
  - priority, flags, critical count
  - stack and switch function
  - accounting ticks
  - locks/limits/refs
  - credentials
  - token stack
  - migration target
  - fd cache
  - compatibility sleepqueue/Linux/FreeBSD fields
  - debug arrays
  - machine-specific thread state
- Defines thread flags, MP flags, thread types, priorities, and stack size.
- Declares global tokens and LWKT scheduling/token/IPI/CPU-sync/thread lifecycle APIs.

Important invariants:
- A thread is owned by the CPU in `td_gd`; foreign CPU manipulation must use CPU/IPI messaging.
- Threads stay on per-CPU LWKT run queues while running.
- `TDF_RUNNING` can clear temporarily during preemption, so users must also consider `TDF_PREEMPT_LOCK`.
- Tokens are reacquired after blocking and are designed to avoid deadlock across arbitrary ordering.
- `LWKT_MAXTOKENS` caps beneficially held token refs at 32.
- `MAXCPUFIFO` is 256 and must remain a power of two.

Research notes:
- This is one of DragonFly’s core scheduler/concurrency headers.
- It encodes the design distinction between per-CPU LWKT scheduling and user process scheduling.
