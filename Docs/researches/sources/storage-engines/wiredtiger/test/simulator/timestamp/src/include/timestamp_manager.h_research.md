# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/timestamp_manager.h

Purpose: declares the timestamp validation singleton used by connection and session simulators.

Important APIs and control flow: public helpers parse config strings into maps, convert between hex strings and decimal timestamps, validate hex strings, validate oldest/stable and connection durable timestamps, and validate read/commit/prepare/session durable timestamps. Private `trim()` supports config parsing. Copy and assignment are deleted.

State and persistence behavior: the manager itself stores no timestamp state; it reads state from `connection_simulator` and `session_simulator` during validation.

Dependencies and integration points: included by simulator source files and depends on `session_simulator.h`.

Risks: singleton is mostly stateless but creates tight coupling to the connection singleton during validation. Config parsing supports only simple comma-separated `key=value` tokens and not full WiredTiger nested config grammar.

Test signals: validation error paths should return `EINVAL` and print descriptive messages through simulator macros.
