# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/validator.h

`validator.h` declares the public interface and state structures for the embedded libunbound DNSSEC validator module. It defines TTL constants for null and bogus key entries plus root-key-sentinel label constants.

`struct val_env` is global validator state: key cache, aggressive negative cache, validation date/skew settings, restart limit, bogus TTL, NSEC3 iteration limits, and a protected bogus-RRset counter. `struct val_qstate` is per-query state: original/chased messages, restart and blacklist state, chased qname, trust-anchor and DS state, current key entry, response classification/signer data, trust-anchor priming flag, signature-suspension cursor, NSEC3 cache table, suspended DS message, and resume timer.

The exported API provides module lifecycle and operation hooks (`val_init()`, `val_deinit()`, `val_operate()`, `val_inform_super()`, `val_clear()`, `val_get_mem()`), state string conversion, suspend timer callback, NSEC3 iteration config parsing, and validator environment config application. It is the header consumed by the resolver and module framework to embed the validator.
