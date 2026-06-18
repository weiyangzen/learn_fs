# sources/storage-engines/wiredtiger/test/suite/helpers/modify_utils.py

Purpose: utility functions for generating randomized old values, modify vectors, and expected new values for WiredTiger modify-operation tests.

Important APIs and control flow: `OpType` enumerates add/remove/replace operations. `create_value()` builds repeated random string or bytes patterns depending on value format `S` or `u`. `create_mods()` chooses sorted offsets, lengths, and operation types, synthesizes a new value from the old value, then calls `wiredtiger.wiredtiger_calc_modify()` to compute modify entries, retrying with a larger size budget if repeated data causes an error.

State and persistence behavior: no filesystem or database state. It consumes randomness from a caller-provided random object and returns `(oldv, mods, newv)`.

Dependencies and integration points: depends on Python `string`, `Enum`, and the WiredTiger Python binding's `wiredtiger_calc_modify`.

Risks: offset/length generation can skip modifications when offsets are too close, so requested `nmod` is an upper bound on intended edits. `rand.sample(range(maxdiff), nmod + 1)` requires `maxdiff >= nmod + 1`. Byte generation uses random choices from encoded ASCII.

Test signals: downstream tests apply returned modify vectors and compare stored values with `newv`.
