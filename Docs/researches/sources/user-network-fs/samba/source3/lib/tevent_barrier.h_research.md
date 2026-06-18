## sources/user-network-fs/samba/source3/lib/tevent_barrier.h

Purpose: public interface for the tevent barrier primitive implemented in `tevent_barrier.c`.

Important APIs: opaque `struct tevent_barrier`, `tevent_barrier_init(TALLOC_CTX *, unsigned count, trigger_cb, private_data)`, `tevent_barrier_wait_send`, and `tevent_barrier_wait_recv`. The send/recv shape follows Samba tevent request conventions.

Control flow contract: callers allocate a barrier with a nonzero waiter count, issue wait requests on event contexts, and complete each request through the normal tevent callback/recv path once the barrier trips. The optional trigger callback runs when the barrier releases a full group or when destruction releases pending waiters.

State and persistence: all state is in the opaque talloc object and request objects. The header depends on `talloc.h` and `tevent.h` only.

Risks and tests: the header does not state whether the barrier is reusable, but the implementation resets count after release, so users may rely on that behavior. It also does not document cancellation limits or max simultaneous waiters. API tests should verify send/recv error semantics, zero-count initialization returning NULL, and lifetime interactions between barrier and wait requests.
