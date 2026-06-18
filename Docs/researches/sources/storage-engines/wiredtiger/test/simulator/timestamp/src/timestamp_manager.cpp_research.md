# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/timestamp_manager.cpp

Purpose: implements config parsing, timestamp conversion, and timestamp rule validation for the simulator.

Important APIs and control flow: `parse_config()` splits comma-separated tokens into a map, drops explicitly unsupported keys, and rejects keys not listed as supported. `validate_hex_value()` rejects strings longer than 16 hex digits, non-hex characters, and zero. `validate_oldest_and_stable_timestamp()` enforces monotonic oldest/stable movement and oldest <= stable. Session validators enforce read-before-prepare and single-read rules, commit monotonicity and oldest/stable/latest-read constraints, prepare ordering and stable/latest-read constraints, and durable requirements for prepared transactions.

State and persistence behavior: no internal persistent state. Validation reads current global state from `connection_simulator` and transaction state from passed sessions.

Dependencies and integration points: central rule engine for `connection_simulator::set_timestamp` and all session timestamp setters.

Risks: parser is intentionally simpler than WiredTiger config parsing and may mishandle nested configs beyond current use. `trim()` assumes nonempty strings with at least one non-space character. Stable timestamp validation requires new stable to be strictly greater than current stable, which should match intended simulator behavior.

Test signals: successful and failing call-log replay entries validate rule parity; manual CLI `print_rules()` text should stay synchronized with this implementation.
