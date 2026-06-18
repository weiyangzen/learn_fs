# sources/storage-engines/foundationdb/bindings/python/tests/tuple_tests.py

Purpose: This randomized test validates Python tuple-layer encoding, decoding, lexicographic ordering, comparison, and range behavior.

Important APIs and types: It imports `pack`, `unpack`, `compare`, `int2byte`, `SingleFloat`, and `fdb.tuple.range`. Helpers generate random Unicode, binary strings, integers up to tuple-layer limits, floating edge cases, booleans, UUIDs, and nested lists.

Control flow: `tupleTest` generates random tuples, compares sorting by tuple comparator with sorting by packed bytes, checks pack/unpack identity, verifies prefix ranges include extended tuples but exclude unrelated tuples, and ensures packed-byte ordering matches `compare`.

State and persistence behavior: It is pure in-memory testing; no database state is touched. Its target is persistent key-format compatibility of `fdb.tuple`.

Dependencies and integration points: It depends on Python `random`, `struct`, `ctypes`, `unicodedata`, `uuid`, and tuple-layer implementation details. It can be run as a standalone script.

Risks: The test is probabilistic and seeded only by default runtime state, so it may miss rare edge cases. It uses Python 2-era `sorted(..., cmp=compare)` syntax, which is not valid in modern Python 3 without adaptation.

Test signals: Sort equivalence, pack/unpack identity, prefix range inclusion/exclusion, and comparison parity across thousands of generated tuples are the important signals.
