# sources/object-store/openstack-swift/swift/__init__.py

## Purpose
Defines Swift package version discovery for installed packages and source checkouts.

## Important APIs, Types, and Functions
Module globals `__version__` and `__canonical_version__` are populated. The code first tries `importlib.metadata.distribution('swift')`; on older Python it falls back to `pkg_resources`; if no installed distribution metadata exists, it uses `pbr.version.VersionInfo('swift')`.

## Control Flow
Import-time control flow selects the lightest available version source: installed package metadata first, then pbr for source checkouts. Missing distribution metadata is tolerated until the pbr fallback.

## State and Persistence Behavior
No persistent state is written. The module exposes version strings used by other Swift code, CLI output, packaging, or logs.

## Dependencies and Integration Points
Depends on Python packaging metadata APIs and `pbr`. It integrates at package import time, so broken packaging metadata or missing pbr in source mode can make importing `swift` fail.

## Risks and Test Signals
Import-time dependency on pbr is a risk for incomplete development environments. Test signal is importing `swift` from both installed and checkout contexts and seeing valid version strings.
