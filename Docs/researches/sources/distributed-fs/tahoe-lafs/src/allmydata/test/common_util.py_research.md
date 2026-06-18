<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_util.py -->
## sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_util.py

Purpose: Collects general test utilities for CLI execution, random byte mutation, Deferred-friendly failure assertions, signal/reactor cleanup, and timezone manipulation.

Important APIs and types: `skip_if_cannot_represent_filename`, `run_cli_native`, `run_cli_unicode`, `run_cli`, and `parse_cli` exercise Tahoe CLI code in-process. `DevNullDictionary`, `insecurerandstr`, `flip_bit`, and `flip_one_bit` support mutation tests. `ReallyEqualMixin`, `SignalMixin`, `StallMixin`, `FakeCanary`, `ShouldFailMixin`, `TestMixin`, and `TimezoneMixin` provide reusable test behaviors.

Control flow: CLI helpers construct argv, wrap stdin/stdout/stderr in `TextIOWrapper`/`BytesIO`, parse options, dispatch through `runner.dispatch`, and convert normal completion or `SystemExit` to `(rc, stdout, stderr)`. `ShouldFailMixin.shouldFail` runs a callable through `maybeDeferred`, traps expected Failures, checks message substrings, and returns a list-wrapped Failure for later inspection. `TestMixin.clean_pending` cancels delayed calls and optionally fails if the reactor was not quiescent.

State and persistence: Mutates process-level signal handlers for SIGCHLD, reactor delayed calls during cleanup, and `TZ` environment variable during timezone tests. CLI execution is in-process and does not spawn a separate Tahoe binary.

Dependencies and integration points: Depends on Twisted reactor/failure/Trial, Tahoe CLI runner, encoding utilities, and assertion helpers. `FakeCanary` imitates Foolscap disconnect notification for storage tests.

Risks: `clean_pending` cancels all delayed calls visible to the global reactor and can hide ownership bugs when used permissively. `run_cli_native` defaults encoding from `sys.stdout` and may not perfectly match subprocess behavior. `flip_bit`/`flip_one_bit` assume non-empty byte slices. Timezone restoration deletes `TZ` when originally absent and requires cleanup ordering.

Test signals: Cover CLI success and `SystemExit` paths, Unicode argv/stdin encodings, Deferred and synchronous failure assertions, canary disconnect ordering, signal handler restoration, reactor quiescence enforcement, and timezone restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/common_util.py -->
