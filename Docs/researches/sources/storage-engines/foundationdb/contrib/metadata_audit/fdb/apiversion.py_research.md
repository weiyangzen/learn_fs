# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/apiversion.py

## Purpose
`apiversion.py` supplies version constants for the vendored FoundationDB Python binding used by the metadata audit tools. It intentionally sets a generous upper-bound `LATEST_API_VERSION` while documenting that the real maximum is obtained from the loaded C library at runtime by `fdb.__init__.api_version()`.

## Important APIs, Types, And Functions
The file contains two constants and no functions or classes:

`LATEST_API_VERSION = 740` is a high upper-bound value meant not to block current or near-future FDB versions before the runtime C library is queried.

`FDB_VERSION = "7.3"` is the package version string exported through `fdb.__version__`.

## Control Flow
There is no dynamic control flow. `fdb/__init__.py` imports this module during package import and copies the constants into package-level `__version__` and `LATEST_API_VERSION`.

## State And Persistence Behavior
The module has no mutable state and performs no persistence. Its values are process constants after import. Runtime API compatibility is not decided here; this file only provides a loose advertised ceiling and display version.

## Dependencies And Integration Points
The only direct integration point is `sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/__init__.py`, which imports `FDB_VERSION` and `LATEST_API_VERSION`. The comment aligns with the modified initializer behavior that calls `fdb.impl._capi.fdb_get_max_api_version()` before selecting an API version.

## Risks And Edge Cases
Because `LATEST_API_VERSION` is deliberately higher than the nominal `FDB_VERSION` string, callers that treat it as authoritative rather than as a pre-check ceiling could be misled. The local initializer mitigates this by comparing requested API versions to `libfdb_c` at runtime. If FoundationDB API versions advance past 740, this file could again become a blocker unless updated.

## Test Signals
Tests should verify that importing `fdb` exposes `__version__ == "7.3"` and `LATEST_API_VERSION == 740`, and that selecting an API version above the installed C library maximum fails in `api_version()` despite this high constant. This confirms that runtime C-library discovery, not this static file, controls actual compatibility.
