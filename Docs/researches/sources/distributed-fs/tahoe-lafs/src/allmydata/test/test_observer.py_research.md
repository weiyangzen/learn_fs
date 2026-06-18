# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_observer.py

## Purpose
Tests Tahoe observer-list utilities for one-shot notification, lazy one-shot results, reusable observer fanout, reentrant mutation, error isolation, and `KeyboardInterrupt` propagation.

## APIs / Types / Functions
- `nextTurn` waits one reactor turn.
- `observer.OneShotObserverList` fires once with a stored result.
- `observer.LazyOneShotObserverList` fires once from a result factory.
- `observer.ObserverList` manages subscribers and notifications.

## Control Flow
One-shot tests register waiters, fire results, verify late subscribers get the same result, and confirm repeated `fire_if_not_fired` calls are ignored. Observer-list tests subscribe/unsubscribe callbacks, notify with args/kwargs, validate reentrant self-unsubscribe, ensure normal exceptions are logged without blocking later observers, and assert `KeyboardInterrupt` escapes.

## State And Persistence
All state is in-memory callback lists and observed-value lists. Some assertions wait on the reactor; no persistent state exists.

## Dependencies / Integration Points
Integrates Twisted Deferreds/reactor with Tahoe observer primitives used by asynchronous workflows.

## Risks And Test Signals
Duplicate subscriptions, absent unsubscriptions, and lazy factory errors are not covered. Passing tests show idempotent one-shot behavior, late-subscriber delivery, safe reentrant mutation, isolated normal observer errors, and non-swallowed interrupts.
