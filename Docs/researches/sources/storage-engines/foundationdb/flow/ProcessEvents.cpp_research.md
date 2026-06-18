# sources/storage-engines/foundationdb/flow/ProcessEvents.cpp research

## Purpose

`ProcessEvents.cpp` implements a small process-local event registry for Flow. Callers can register RAII `ProcessEvents::Event` callbacks for one or more `StringRef` event names, trigger events with arbitrary `std::any` data and a Flow `Error`, and create uncancellable callbacks that intentionally live for process lifetime. The implementation is designed to be safe when callbacks add or remove events during a trigger, including reentrant triggers.

## Important APIs, types, and functions

The public API is `ProcessEvents::Event`, `ProcessEvents::uncancellableEvent`, and `ProcessEvents::trigger`. `EventImpl` stores the subscribed names and callback and uses its object address as a stable `Id`. `ProcessEventsImpl` owns `events`, an `unordered_map<StringRef, unordered_map<EventImpl::Id, EventImpl*>>`, plus deferred mutation maps `toRemove` and `toInsert`. The nested `Triggering` RAII helper increments the trigger depth on construction and, when the outermost trigger exits, applies pending removals and insertions back to `events`.

## Control flow

Constructing an `Event` allocates `EventImpl`, which immediately registers itself for every name. Destroying an `Event` removes the implementation from the registry and deletes it. If no trigger is active, add/remove operations mutate `events` directly. If a trigger is active, adds go to `toInsert`, and removes either erase a not-yet-visible pending insertion or record the event id/name list in `toRemove`.

`trigger(name, data, e)` creates a `Triggering` guard, finds callbacks registered for the name, and invokes each callback unless its id is already in `toRemove`. Callback exceptions are forbidden; any exception trips `UNSTOPPABLE_ASSERT(false)`. When nested triggers unwind to depth zero, `Triggering::~Triggering` removes deferred ids from each named event map, clears `toRemove`, merges all `toInsert` callbacks into `events`, and clears `toInsert`.

## State and persistence behavior

All state is process-local in the static `processEventsImpl`. There is no durable persistence. `uncancellableEvent` intentionally leaks an `EventImpl` by allocating it without a returned owner, making the callback live until process termination. Normal `Event` objects are RAII-managed and non-copyable. `StringRef` names are stored by value as references to external bytes, so callers must use stable string storage such as string literals or other lifetime-safe strings.

## Dependencies and integration points

The implementation depends on `flow/ProcessEvents.h`, Flow `StringRef`, `Error`, `NonCopyable`, assertions, and `UnitTest`. It uses STL `std::any`, `std::function`, `std::vector`, `std::unordered_map`, and `std::map`. It can be integrated by subsystems that need lifecycle hooks or process-wide notifications without introducing actor scheduling.

## Risks and edge cases

The biggest risk is lifetime: registered event names are `StringRef`s, not owning strings. Using temporary strings as event names would leave dangling references in the registry. The registry is not synchronized; it assumes single-threaded or externally serialized use. Mutating the callback map while iterating is handled through deferred maps, but callback ordering is unspecified because callbacks are stored in unordered maps. Exceptions in callbacks are fatal by assertion. `events[name].erase(id)` in removal paths can create empty maps for missing names; this is harmless but may leave empty event-name entries.

## Test signals

The inline unit test covers basic trigger delivery, adding callbacks during a trigger and verifying they do not run until later triggers, callbacks registered for multiple names, self-removal during a trigger, non-deleted callbacks continuing to run, and reentrant triggering with a temporary callback that must not run during the active trigger. Additional tests should cover destruction before first trigger, removal of a pending inserted event, uncancellable lifetime behavior, and invalid callback exception handling in debug builds.
