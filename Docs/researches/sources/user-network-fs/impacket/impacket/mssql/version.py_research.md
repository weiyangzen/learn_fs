# sources/user-network-fs/impacket/impacket/mssql/version.py

## Purpose
`mssql/version.py` parses the four-byte SQL Server version field returned in the TDS pre-login response and provides a human-readable SQL Server product/update label. It is used by `impacket/tds.py` after `TDS_PRELOGIN` parsing to populate `self.mssql_version`.

## Important APIs, Types, and Functions
The file exports `MSSQL_VERSION`. `VERSION_NAME` is a nested static lookup shaped as `("Microsoft SQL Server", {major: (major_name, {minor: (minor_suffix, {build: update_label})})})`. It includes historical versions from SQL Server 6.0 and 6.5 through 2022 build entries present at the time this table was authored.

`__init__(self, version)` unpacks the supplied bytes with `struct.unpack_from(">bbH", version)`, storing signed one-byte `major`, signed one-byte `minor`, and unsigned big-endian two-byte `build`. `version_number` returns `"{major}.{minor}.{build}"`. `version_name` walks the nested table and returns a string such as `Microsoft SQL Server 2019 (CU20)` when all keys are known. `__repr__()` returns the display name followed by the numeric version in parentheses.

## Control Flow
The normal control path is `tds.MSSQL.preLogin()`: send a TDS pre-login packet, parse the response as `TDS_PRELOGIN`, then call `MSSQL_VERSION(response["Version"])`. After construction, callers can render `repr(mssql_version)` or inspect `version_number` and `version_name`.

The `version_name` property starts with the root string, appends the major version label, minor suffix, and build label in order, and suppresses `KeyError` for unknown major/minor/build table entries. It returns from a `finally` block.

## State and Persistence Behavior
Instances are immutable in practice after `major`, `minor`, and `build` are assigned, though the attributes are public and can be reassigned. The class has no I/O, persistence, caching, or network behavior. The large static `VERSION_NAME` table is process-global and mutable because it is a normal class attribute.

## Dependencies and Integration Points
The only import is Python `struct`. The direct integration point is `impacket/tds.py`, which imports `MSSQL_VERSION` and sets `self.mssql_version` during pre-login. Downstream SQL tools can use that value for banners, logging, compatibility decisions, or diagnostics after connecting to a server.

## Risks and Edge Cases
The `version_name` property has a correctness bug for unknown major versions: if `MSSQL_VERSION.VERSION_NAME[1][self.major]` raises before `string` is assigned, the `finally` block attempts to return an unbound local variable. Unknown minor or build values return a partial name because `string` has already been initialized and partly appended. The code catches only `KeyError`, so malformed `VERSION_NAME` structure would raise other exceptions.

`struct.unpack_from(">bbH", version)` requires at least four bytes; shorter pre-login version fields raise `struct.error`. The signed byte format is harmless for current SQL Server major/minor values but semantically odd for protocol version bytes. The static build table can become stale as new SQL Server cumulative updates ship, so a current server can produce only a partial `Microsoft SQL Server 2022` style label or fail for a new major release. The table also has no metadata indicating source date.

## Test Signals
Unit tests should parse known four-byte values for representative versions: SQL Server 2000, 2005, 2012, 2019 CU entries, and 2022 entries. Tests should assert `version_number`, `version_name`, and `repr()`. Negative tests should include unknown build for a known major/minor, unknown minor for a known major, unknown major, and too-short byte strings. The unknown-major test should document or fix the current unbound-local behavior. Integration tests should verify `tds.MSSQL.preLogin()` stores an `MSSQL_VERSION` object from a mocked `TDS_PRELOGIN` response.
