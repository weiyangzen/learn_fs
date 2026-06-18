<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ProcessEvents.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ProcessEvents.h

Purpose: This header defines a lightweight process-local event callback mechanism. It lets code register callbacks for named events and trigger them with typed-erased data plus a Flow `Error`.

Important APIs and types: `ProcessEvents::Callback` is `std::function<void(StringRef, std::any const&, Error const&)>`. `ProcessEvents::Event` is an RAII registration object constructed with one name or a vector of names. Free functions are `uncancellableEvent` and `trigger`.

Control flow: Creating an `Event` registers callbacks through an opaque implementation pointer; destroying it unregisters. `uncancellableEvent` registers a callback that is not tied to RAII cancellation. `trigger` dispatches by name and passes the event name, payload, and error to subscribers. Comments specify callbacks must not throw; this is enforced at runtime in implementation.

State and persistence behavior: State is process-local subscription state hidden behind `impl`; no data is persisted. Payload state is carried in `std::any`, so producers and consumers must agree on types out of band.

Dependencies and integration points: The header depends on `flow/flow.h`, `std::function`, and `std::any`. It integrates with trace process-event hooks and any subsystem that needs local lifecycle or diagnostic notifications without wiring direct dependencies.

Risks: Runtime type erasure can produce bad casts in subscribers. Callback exceptions are prohibited but only caught/enforced by implementation. RAII unregistration means storing `Event` objects in short-lived scopes can silently remove subscriptions too early.

Test signals: Tests should validate registration and unregistration, multi-name event registration, uncancellable callback lifetime, payload delivery with expected `std::any` type, error delivery, and behavior when callbacks throw.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ProcessEvents.h -->
