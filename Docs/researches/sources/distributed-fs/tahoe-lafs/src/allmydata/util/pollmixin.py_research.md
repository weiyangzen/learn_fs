# sources/distributed-fs/tahoe-lafs/src/allmydata/util/pollmixin.py

## Purpose

This module provides a Deferred-returning polling mixin mostly for tests. It repeatedly calls a predicate until it succeeds, times out, or observes unexpected logged errors.

## APIs and control flow

`PollMixin.poll(check_f, pollinterval=0.01, timeout=1000)` starts a Twisted `LoopingCall` around `_poll()`. `_poll()` raises local `TimeoutError` after the cutoff, raises `PollComplete` when `check_f()` returns true, and, in Trial-style tests, inspects `self._observer.getErrors()` to fail early on unexpected logged errors. `poll()` converts `PollComplete` into a successful `None` result.

## State, dependencies, risks, and tests

State is the running LoopingCall and optional `_poll_should_ignore_these_errors` on the test object. Dependencies are Twisted `task.LoopingCall` and wall-clock `time.time`.

Risks include wall-clock sensitivity, predicate exceptions errbacking directly, ignored error type lists being too broad or too narrow, and long default timeouts hiding hangs. Test signals should cover immediate success, delayed success, timeout, predicate exception propagation, observed-error early failure, ignored errors, and `timeout=None` behavior.
