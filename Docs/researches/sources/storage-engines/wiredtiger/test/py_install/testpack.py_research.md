# sources/storage-engines/wiredtiger/test/py_install/testpack.py

Purpose: installation sanity test for the Python packing-only API. It validates that `wiredtiger.packing.unpack` and `pack` are importable and produce expected binary/int conversions.

Important APIs and control flow: builds bytes from a fixed hexadecimal string, unpacks it with format `iiiiiiiiiiiiii`, compares the resulting integer list to a hard-coded expected sequence, packs four integers with format `iiii`, and compares the exact byte string to `b'\x81\x82\x83\x84'`.

State and persistence behavior: no database or filesystem state is used. All validation is in process memory.

Dependencies and integration points: depends on `wiredtiger.packing` from the installed Python package. It intentionally avoids `wiredtiger_open` and therefore isolates packing module installation from full database runtime setup.

Risks: hard-coded byte encodings are sensitive to packing format semantics; if the encoding changes intentionally, this test must be updated. It retains Python 2/3 compatibility style around byte construction although modern runs are likely Python 3.

Test signals: exceptions indicate exact pack/unpack mismatch; success prints `testpack success.`
