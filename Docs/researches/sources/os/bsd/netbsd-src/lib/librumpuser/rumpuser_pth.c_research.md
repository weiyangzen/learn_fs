# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_pth.c

## Purpose
Implements the pthread-backed rumpuser threading and synchronization layer used by rump kernels on hosts with POSIX threads.

## Main Interfaces
Provides `rumpuser_thread_create`, `rumpuser_thread_exit`, `rumpuser_thread_join`, mutex APIs, rwlock APIs, condition-variable APIs, `rumpuser_curlwpop`, `rumpuser_curlwp`, and `rumpuser__thrinit`.

## Control Flow And State
Thread creation configures joinable or detached pthread attributes, retries `pthread_create` on `EAGAIN`, and optionally sets thread names via platform-specific `pthread_setname_np` variants. Joinable threads allocate a `pthread_t` cookie that is freed after successful join.

Mutexes wrap `pthread_mutex_t` with error-checking attributes, explicit lock alignment, rump-kernel lock flags, and a tracked `struct lwp *owner` for kernel mutexes. Non-spin mutex acquisition uses `KLOCK_WRAP` around blocking pthread lock calls, while spin-style entry uses the nowrap path.

Rwlocks wrap `pthread_rwlock_t` and track reader count, writer LWP, and downgrade-in-progress state. Writer acquisition loops around `rw_setwriter()` to avoid returning a writer lock while another holder is downgrading. Reader counts use native atomics on NetBSD/Apple/Android and a pthread spinlock elsewhere.

Condition variables track waiter counts and carefully unschedule/reschedule rump kernel CPU context around `pthread_cond_wait`. The spin-mutex CV reschedule path releases the pthread mutex before reacquiring kernel scheduling context to avoid lock-order deadlock.

Current LWP identity is stored in pthread thread-local storage. The active implementation stores the raw `struct lwp *`; an `#if 0` alternate list-backed validator remains as test/debug scaffolding.

## Dependencies
Depends on pthreads, `aligned_alloc`, `nanosleep`, `clock_gettime`, atomic support where available, rumpuser public/internal headers, and rump kernel scheduling hooks such as `rumpkern_sched` and `rumpkern_unsched`.

## Risks And Notes
The rwlock downgrade protocol is subtle: writers may briefly acquire the underlying pthread lock but must not return to the caller while `downgrade` is set. CV waits depend on precise mutex owner bookkeeping around pthread wait unlock/relock behavior. Timed waits use `CLOCK_REALTIME`, so wall-clock changes can affect timeout behavior.
