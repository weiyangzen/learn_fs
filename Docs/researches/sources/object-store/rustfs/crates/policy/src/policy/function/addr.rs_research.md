<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/addr.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/addr.rs

Purpose: Implements IP address condition values and evaluation for `IpAddress` and, through `Condition` negation, `NotIpAddress`.

Important APIs/types/functions: `AddrFunc` is `InnerFunc<AddrFuncValue>`. `AddrFunc::evaluate(values)` checks request context IP values against configured CIDR networks. `AddrFuncValue(Vec<IpNetwork>)` deserializes from a string or string array and serializes transparently.

Control flow: For each configured key/value pair, evaluation looks up request values by the condition key's short name, parses each request string as `IpAddr`, and returns true as soon as any IP is contained in any configured network. If a request value cannot parse, it returns false. If there are no matching request values across all configured entries, it returns false. Deserialization appends `/32` to values without a slash before parsing as `IpNetwork`.

State/persistence behavior: Stateless in memory; persisted policy values are CIDR strings or arrays. Serialization normalizes single string inputs to arrays because `IpNetwork` vec is transparent and tests expect arrays.

Dependencies/integration: Uses `ipnetwork` with serde, `InnerFunc`, `Key`, and `KeyName`. `Condition::NotIpAddress` inverts `AddrFunc::evaluate` through `is_negate`.

Risks/test signals: Appending `/32` to IPv6 host literals means host IPv6 values become `/32`, which is a broad IPv6 network rather than the usual `/128`; tests encode this behavior but it may not match AWS semantics. Evaluation returns true on the first matching configured key and does not require all `InnerFunc` entries to match. Tests cover IPv4/IPv6 CIDR and host parsing, variables, arrays, and serialization.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/addr.rs -->
