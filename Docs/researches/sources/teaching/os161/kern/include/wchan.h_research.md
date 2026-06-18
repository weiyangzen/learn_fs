# File Research: sources/teaching/os161/kern/include/wchan.h

Declares opaque wait channels used to block and wake threads. A wait channel has a symbolic name, creation/destruction calls, diagnostic emptiness check, sleep, wake-one, and wake-all operations.

The sleep API requires the associated spinlock to be held. `wchan_sleep` atomically releases that lock while sleeping and reacquires it before returning. Wake APIs expect the spinlock to be held; FIFO behavior is current implementation detail, not an interface promise.

This header underpins semaphores and likely other blocking primitives. Correctness depends on using the same lock to protect the condition being waited on and avoiding sleep from interrupt context.
