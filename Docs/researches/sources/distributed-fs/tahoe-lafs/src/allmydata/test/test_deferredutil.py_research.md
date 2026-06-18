# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_deferredutil.py

## Purpose
This module tests Tahoe utility wrappers around Twisted Deferreds, including gathering behavior, delayed-call cleanup, retry-until loops, async coroutine adaptation, and a `race` helper that resolves on the first success or aggregates failures.

## Important APIs, types, and functions
- `DeferredUtilTests` covers `deferredutil.gatherResults`, `DeferredListShouldSucceed`, and `WaitForDelayedCallsMixin.wait_for_delayed_calls`.
- `UntilTests` covers `deferredutil.until`.
- `AsyncToDeferred` covers the `async_to_deferred` decorator.
- `_setupRaceState` builds cancellable Deferreds and cancellation counters.
- `RaceTests` covers `race` and `MultiFailure` using Hypothesis-generated before/after counts.

## Control flow
Gather/list tests create Deferreds manually, fire callbacks or errbacks in controlled order, and assert the aggregate result. `until` tests verify synchronous exceptions, repeated synchronous calls until a condition flips, and waiting for Deferred completion before the next iteration. `async_to_deferred` wraps async functions and inspects the resulting Deferred for success or captured exception. Race tests set up N Deferreds, trigger one success or all failures, and inspect the result Deferred plus cancellation side effects.

## State and persistence behavior
There is no filesystem persistence. State is held in Deferred callback chains, lists that record successes/failures/cancellation counts, and Twisted's reactor delayed-call queue. The delayed-call test specifically ensures pending calls are waited out so Trial does not report an unclean reactor.

## Dependencies and integration points
Dependencies include Twisted Trial, Twisted reactor and Deferred APIs, `twisted.python.failure.Failure`, Hypothesis integer strategies, and Tahoe `deferredutil`. The tests integrate Tahoe's Deferred helpers with Trial's synchronous and asynchronous result helpers.

## Risks
Cancellation semantics are subtle. `race` must cancel losers after a success, ignore later results from cancelled Deferreds without logged errors, tolerate cancellers that callback, and convert full failure or result cancellation into `MultiFailure`. `until` can spin if the action never returns a Deferred and condition never becomes true; the tests cover only bounded examples.

## Test signals
Signals include immediate errback propagation from gathered results, success-only list aggregation, failure wrapping as `Failure`, delayed-call drain behavior, `until` exception/result sequencing, coroutine success and exception adaptation, `race` winner index/result, loser cancellation counts, aggregate `MultiFailure.failures`, no logged errors for post-cancel results, and cancellation propagation to all inputs.
