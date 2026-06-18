<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/OwningResource.h -->
# sources/storage-engines/foundationdb/flow/include/flow/OwningResource.h

Purpose: This header provides weak/owning resource references for actor lifetimes. It solves the pattern where a parent actor owns context state while spawned actors may run after the parent releases that state.

Important APIs and types: Internal `details::Resource<T>` owns a raw `T*` inside a reference-counted wrapper. `details::ResourceRef<T>` implements `operator->`, `operator*`, and `available`. Public types are `ResourceOwningRef<T>`, `ResourceWeakRef<T>`, `ActorOwningSelfRef<T>`, and `ActorWeakSelfRef<T>`.

Control flow: An owning ref creates the shared `Resource<T>`. Weak refs share the wrapper but not ownership of the underlying object. Destroying `ResourceOwningRef` resets the wrapper's resource pointer to null, which causes weak `available()` checks to fail. `ActorWeakSelfRef` converts unavailable access into `operation_cancelled`, suitable for terminating actors.

State and persistence behavior: State is purely in-memory and process-local. No persistence is involved. `Resource<T>::reset` deletes the old resource and stores the replacement pointer; owning destruction resets to null rather than deleting the wrapper so weak refs can observe unavailability.

Dependencies and integration points: It depends on `FastRef`, `ReferenceCounted`, `NonCopyable`, and Flow error types. It is integrated with long-lived role `self` objects and child actors that must avoid use-after-free when parent actors exit.

Risks: Raw pointer ownership means callers must pass heap objects intended to be deleted by the wrapper. `ResourceRef::operator->` does not check availability, so generic weak users must call `available()` first unless using `ActorWeakSelfRef`. Copy and assignment operators in internal refs are narrow and should not be extended casually.

Test signals: Tests should cover weak availability before and after owner destruction, `ActorWeakSelfRef` throwing `operation_cancelled`, `ResourceRef::operator*` throwing `internal_error` when unavailable, and deletion/reset behavior with instrumented objects.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/OwningResource.h -->
