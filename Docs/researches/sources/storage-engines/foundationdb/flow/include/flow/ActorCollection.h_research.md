# sources/storage-engines/foundationdb/flow/include/flow/ActorCollection.h

Purpose: declares `actorCollection` and convenience wrappers for managing dynamically added actor futures.

Important APIs/types/functions: `actorCollection`, `ActorCollectionNoErrors`, `ActorCollection`, and `SignalableActorCollection`.

Control flow: declared `actorCollection` consumes a `FutureStream<Future<Void>>`, cancels child futures deterministically on cancellation, returns errors immediately, and optionally returns when the collection empties. Wrappers send futures through `PromiseStream` and expose size/result/signal operations.

State/persistence: wrappers hold `PromiseStream`, result future, optional count, and stop promise. No durable persistence.

Dependencies/integration: includes `flow/flow.h`; used by higher-level actor systems that need dynamic supervision.

Risks: lifecycle is cancellation-sensitive. `ActorCollectionNoErrors` assumes child actors report errors themselves. `SignalableActorCollection` uses a stop future to force emptying and reset/collapse semantics that callers must understand.

Test signals: indirect through actor supervision tests and production actor cancellation/error handling.
