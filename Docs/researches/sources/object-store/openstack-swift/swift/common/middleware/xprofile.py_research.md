# sources/object-store/openstack-swift/swift/common/middleware/xprofile.py

## Purpose
`xprofile.py` implements Swift's profiling WSGI middleware. It profiles normal application requests, periodically dumps profile data to disk, and exposes a small unauthenticated development UI/API under a configurable path such as `/__profile__`. The module docstring warns it is intended for development and testing, not production.

## Important APIs, types, and functions
`ProfileMiddleware(app, conf)` is the WSGI filter. It parses configuration such as `log_filename_prefix`, `dump_interval`, `dump_timestamp`, `flush_at_shutdown`, `path`, `unwind`, and `profile_module`. `__call__()` dispatches favicon requests, profile UI/API requests, and normal application requests. `_combine_body_qs()` merges request query parameters with URL-encoded POST body fields. `dump_checkpoint()` schedules periodic `ProfileLog.dump_profile()` calls. `renew_profile()` reinstantiates the configured profiler. `get_profiler(profile_module)` imports and creates a profiler, monkey-patching eventlet profile behavior when needed. `filter_factory()` is the paste-deploy entry point.

The module also defines `new_setup()`, `new_runctx()`, and `new_runcall()` monkey patches for `eventlet.green.profile.Profile`, plus two code strings: eager profiling consumes and closes the app iterator, lazy profiling profiles only iterator construction.

## Control flow and state behavior
Initialization creates the profile directory if missing, gets a Swift logger, constructs `ProfileLog` and `HTMLViewer`, creates a large green pool for asynchronous dumps, and delays the first dump until a request arrives. For profile UI requests, `__call__()` dumps a checkpoint, combines query/body parameters, calls `viewer.render()`, translates profile exceptions to HTTP status codes, encodes string content to bytes, and returns a one-element body list. For non-profile requests, the middleware runs either eager or lazy app execution under `self.profiler.runctx()`, then dumps a checkpoint and returns the profiled iterator.

Persistent state is the profile dump files written by `ProfileLog`. Runtime state includes the profiler object, dump timing, and green-pool tasks. `flush_at_shutdown` is unusual: `__del__()` clears the current process profile rather than forcing a dump.

## Dependencies and integration points
The middleware integrates with Swift WSGI paste configuration, `swift.common.swob.Request`, `swift.common.utils.get_logger`, `config_true_value`, eventlet concurrency/profile modules, and the x_profile viewer/model classes. Its output files are later parsed by `Stats2` and exposed by `HTMLViewer`. It uses the original `_thread` module via eventlet patcher to avoid monkey-patched thread identity in profiler setup.

## Risks and edge cases
The UI has no authentication, exposes profiling data, and accepts clear requests, so deployment in production is risky. `_combine_body_qs()` reads the entire request body for profile POSTs. Lazy mode may miss work done during iterator consumption; eager mode changes streaming behavior and resource use by materializing the entire app iterator. Monkey-patching eventlet profiler methods is process-global. `__call__()` returns plain strings in some error paths, which may rely on WSGI/server tolerance. Directory creation can fail on permissions. Asynchronous dump tasks may overlap under high request rates if dump intervals are small.

## Test signals
Tests should cover paste factory construction, normal request profiling in lazy and eager modes, profile path routing, exception-to-status mapping, dump throttling, POST body parameter merging, clear-and-renew behavior, eventlet monkey patch installation, directory creation failures, and profiler module import errors.
