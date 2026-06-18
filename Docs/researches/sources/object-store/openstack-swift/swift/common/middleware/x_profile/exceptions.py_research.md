# sources/object-store/openstack-swift/swift/common/middleware/x_profile/exceptions.py

Purpose: Defines the exception taxonomy used by Swift's xprofile profiling middleware and viewer/model helpers. The exceptions provide user-facing profiling error messages and distinguish missing resources, unsupported methods, missing optional plotting/export dependencies, and data-load failures.

Important APIs and types: `ProfileException` is the base class and stores `msg`; its `__str__()` renders `Profiling Error: <msg>`. Derived marker classes are `NotFoundException`, `MethodNotAllowed`, `ODFLIBNotInstalled`, `PLOTLIBNotInstalled`, and `DataLoadFailure`.

Control flow: There is no runtime dispatch in this file beyond exception construction and string conversion. Other xprofile modules raise these classes and catch `ProfileException` or specific subclasses to map profiling failures to HTTP responses or rendered error pages.

State and persistence: The only state is the per-exception `msg` attribute. No durable state or global mutable data exists.

Dependencies and integration points: The file has no imports. It is imported by `swift.common.middleware.xprofile`, `x_profile.html_viewer`, and `x_profile.profile_model`. `html_viewer` raises the optional dependency exceptions for odfpy/matplotlib and not-found/data-load cases; `xprofile` catches `NotFoundException` and generic `ProfileException` while serving profiling endpoints.

Risks: These exceptions do not call `Exception.__init__()`, so code that relies on standard `args` may not see the message. This is existing behavior but should be considered before adding serialization or logging integrations. Messages may be shown to clients, so callers should avoid placing sensitive data in `msg`.

Test signals: Unit tests should assert string formatting, subclass identity, and that xprofile callers map `NotFoundException`, `MethodNotAllowed`, dependency exceptions, and `DataLoadFailure` to the intended HTTP/UI behavior. Optional dependency tests should monkeypatch imports rather than requiring odfpy or matplotlib.
