# sources/object-store/rustfs/crates/config/src/audit/mysql.rs

## Purpose
Declares MySQL audit target config keys and environment variables.

## Important APIs, types, and functions
`AUDIT_MYSQL_KEYS` covers enablement, DSN string, table, format, TLS CA/client cert/client key, queue directory/limit, max open connections, and comments. `ENV_AUDIT_MYSQL_*` and `ENV_AUDIT_MYSQL_KEYS` expose matching environment names except comments.

## Control flow
No executable flow; downstream config code consumes the key lists.

## State and persistence behavior
Static constants only.

## Dependencies and integration points
References shared MySQL key constants and is re-exported through the audit module. MySQL audit storage/publisher code should use these keys to configure connection pooling and durable queues.

## Risks and edge cases
DSN and TLS key values are sensitive downstream. This file does not validate table names, format names, queue limits, or connection counts. Env/config arrays must stay aligned with implementation support.

## Test signals
No local tests; coverage should come from audit config parsing and MySQL target initialization tests.
