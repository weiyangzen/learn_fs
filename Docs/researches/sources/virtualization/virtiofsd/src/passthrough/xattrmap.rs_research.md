# File Research: sources/virtualization/virtiofsd/src/passthrough/xattrmap.rs

This file implements extended-attribute name translation between the guest client and host server.

Rule model:
- `Scope`: client, server, or both.
- `Type`: `Prefix`, `Okay`, `Bad`, `Unsupported`, and `Map`.
- `Rule`: scope, type, client-side key prefix, and server-side prepend prefix.
- `XattrMap`: ordered list of expanded rules; first matching rule wins.

Error model:
- `ErrorKind` covers invalid scope/type, invalid delimiter, incomplete rule, `map` rule violations, empty input, and unterminated mappings.
- `Error` wraps `ErrorKind` plus optional 1-based rule number.

Parsing:
- Rules are delimiter-based and may use different delimiters per rule.
- Full form: delimiter, type, scope, key, prepend, delimiter-separated.
- `map` shorthand parses key and prepend, expands to multiple ordinary rules, and must be final.
- Empty input is rejected.
- Whitespace between ordinary rules is skipped.

Mapping behavior:
- `map_client_xattr()` finds a client rule and returns `AppliedRule::Pass`, `Deny`, or `Unsupported`.
- `Prefix` prepends the configured server prefix to a client xattr name.
- `Okay` passes the client name unchanged.
- `Bad` maps to guest `EPERM` at the caller.
- `Unsupported` maps to guest `ENOTSUP` at the caller.
- `map_server_xattrlist()` processes NUL-separated host xattr names, hiding `Bad` and `Unsupported` names, passing `Okay`, and stripping `Prefix` prepends.
- If all server names are filtered, it returns a single NUL byte.

Tests:
- Cover single and multiple rule parsing, whitespace-separated rules, incomplete rules, map-rule violations, map expansion, invalid type/scope, no rules, different delimiters, ok/bad/unsupported behavior, prefix prepend, and server prefix stripping.

Interactions:
- `passthrough/mod.rs` uses this map in `map_client_xattrname()` and `map_server_xattrlist()`.
- The read-only wrapper allows read/list xattr operations to use the same mapping while denying mutation.

Edge cases and risks:
- `CString::new(...).unwrap()` assumes parsed rule fields contain no interior NULs.
- The `InvalidType.expected` string omits `unsupported` even though `unsupported` is accepted.
- The `map` final-rule check happens before trailing whitespace is skipped, so a final `map` rule followed only by whitespace appears likely to be rejected.
