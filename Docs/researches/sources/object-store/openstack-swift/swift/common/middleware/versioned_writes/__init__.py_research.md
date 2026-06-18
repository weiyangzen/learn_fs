# sources/object-store/openstack-swift/swift/common/middleware/versioned_writes/__init__.py

Purpose: Provides the paste filter factory for Swift versioning. It composes the legacy `VersionedWritesMiddleware` with the newer `ObjectVersioningMiddleware` when configured, and registers public capability flags in Swift info.

Important APIs and types: The module imports `CLIENT_VERSIONS_LOC`, `CLIENT_HISTORY_LOC`, and `VersionedWritesMiddleware` from `legacy.py`, plus `ObjectVersioningMiddleware` from `object_versioning.py`. The only local API is `filter_factory(global_conf, **local_conf)`.

Control flow: The factory merges global and local config. If `allow_versioned_writes` is true, it registers `versioned_writes` with allowed flags for `x-versions-location` and `x-history-location`. If `allow_object_versioning` is true, it registers `object_versioning`. The returned `versioning_filter()` wraps the app in `ObjectVersioningMiddleware` first when object versioning is enabled, after verifying that `symlink` is registered in Swift info, then always wraps with `VersionedWritesMiddleware`.

State and persistence: This file persists nothing directly. It controls which middleware layers are in the request path and what capability metadata appears in `/info`.

Dependencies and integration points: Depends on `config_true_value`, `register_swift_info`, and `get_swift_info`. The explicit symlink capability check encodes a hard runtime dependency of object versioning on static symlink support. It is the integration point that allows legacy and new versioning modes to coexist in the configured pipeline while retaining backwards compatibility.

Risks: Middleware wrapping order matters. Object versioning relies on symlink behavior, while legacy versioned writes still needs to run for legacy headers and objects. If `symlink` has not registered itself before this factory runs, enabling object versioning raises `ValueError`. Capability registration is configuration-driven; disabling flags can hide features from clients even if older container-server compatibility behavior remains elsewhere.

Test signals: Validate factory behavior for all config combinations, `/info` capability registration, `ValueError` when object versioning is enabled without symlink, and wrapping order where object versioning is inside legacy versioned writes. Tests should also ensure legacy-only deployments still work when `allow_object_versioning` is false.
