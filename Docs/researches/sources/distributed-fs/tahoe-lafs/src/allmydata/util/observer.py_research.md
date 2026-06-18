# sources/distributed-fs/tahoe-lafs/src/allmydata/util/observer.py

## Purpose

This module implements observer helpers for Twisted-style asynchronous code: one-shot Deferred notifications, lazy result production, immediate multi-subscriber notifications, and buffered event streams for a single subscriber.

## APIs and control flow

`OneShotObserverList.when_fired()` returns an already-succeeded Deferred after firing or stores a watcher before firing. `fire()` records the result and callbacks all watchers exactly once. `LazyOneShotObserverList` stores a result producer instead of retaining the result and only calls it when needed. `ObserverList` maintains callbacks and logs exceptions without stopping notification. `EventStreamObserver` buffers keyword-only events until a subscriber is set, schedules notifications with Foolscap `eventually`, and can call a weakref-based canceler on cancellation.

## State, dependencies, risks, and tests

State is watcher lists, fired/result flags, buffered event kwargs, and weak canceler references. Dependencies are Twisted Deferreds/logger, Foolscap eventual scheduling, and `weakref`.

Risks include one-shot double-fire assertions, retained results causing memory retention unless lazy form is used, event buffering growing unbounded before subscription, weak canceler disappearing, and asynchronous ordering through `eventually`. Test signals should cover pre/post-fire `when_fired`, lazy producer call counts, observer exception logging, unsubscribe, buffered event delivery order, watcher kwargs merge, and canceler invocation.
