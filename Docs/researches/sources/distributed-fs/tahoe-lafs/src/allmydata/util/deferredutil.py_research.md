# sources/distributed-fs/tahoe-lafs/src/allmydata/util/deferredutil.py

## Purpose

This module provides Twisted Deferred utilities for timeouts, DeferredList result normalization, eventual callback chaining, test hooks, polling cleanup, async/coroutine bridging, and racing Deferreds. It is a shared async infrastructure module.

## APIs and control flow

`timeout_call()` races a Deferred result against a reactor timer and raises local `TimeoutError` on expiry. `DeferredListShouldSucceed()` and `gatherResults()` convert DeferredList results into plain lists or first failures. `eventually_callback()`, `eventually_errback()`, and `eventual_chain()` schedule callbacks through Foolscap `eventually` while logging `AlreadyCalledError`.

`HookMixin` lets tests register named one-shot Deferred hooks with ignore counts. `WaitForDelayedCallsMixin` polls the reactor for near-term delayed calls. `until()` repeats a Deferred-returning action until a predicate is true. `async_to_deferred()` wraps async functions into Deferred-returning callables. `race()` returns the first successful Deferred index/value and cancels the rest, or fails with `MultiFailure`.

## State, dependencies, risks, and tests

State is mostly caller-owned Deferreds plus hook dictionaries. Dependencies include Twisted reactor/defer/error, Foolscap eventual scheduling, Eliot inline callbacks, Failure, local logging, and `PollMixin`.

Risks include Deferred cancellation semantics, timer/result races, swallowing AlreadyCalled problems unless logs are checked, `race()` behavior when inputs ignore cancellation, and test hook misuse. Test signals should cover timeout success/failure races, DeferredList failures, hook ignore counts and async mode, delayed-call polling, coroutine conversion, `until()` loops, `race()` first success, all-failure `MultiFailure`, and cancellation propagation.
