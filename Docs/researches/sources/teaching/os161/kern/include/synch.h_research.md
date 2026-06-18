# File Research: sources/teaching/os161/kern/include/synch.h

Declares higher-level synchronization primitives. Semaphores are fully shaped here with a name, wait channel, spinlock, and volatile count, and export `sem_create`, `sem_destroy`, `P`, and `V`.

Locks, condition variables, and reader-writer locks are intentionally skeletal teaching interfaces. `struct lock` includes a name and optional Hangman hook with placeholder fields for students. `struct cv` and `struct rwlock` likewise contain names and placeholders. The exported operations define expected semantics: exclusive locks, Mesa-style CVs, and read/write acquisition/release.

Dependencies include `spinlock.h`, wait channels, current-thread state, and scheduler sleep/wakeup behavior. The main risk is incomplete implementation: correctness depends on atomic sleep/release/reacquire behavior and ownership tracking.
