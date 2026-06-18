# sources/sync-backup/bup/test/int/test_vint.py

Purpose: validates bup variable-length integer, byte-vector, and typed pack/send/recv serialization primitives.

Important APIs/types/functions: `vint.write_vuint`, `read_vuint`, `encode_vuint`, `write_vint`, `read_vint`, `write_bvec`, `read_bvec`, `skip_bvec`, `send`, `recv`, `pack`, `unpack`, `BytesIO`, and `combinations_with_replacement`.

Control flow: helper functions encode then decode unsigned ints, signed ints, and byte vectors. Tests cover negative unsigned rejection, zero/small/huge integers, empty streams returning `None`, truncated continuation bytes raising `EOFError`, byte-vector concatenation and skipping, bad format strings and argument count errors for `send/recv`, and all pair combinations of candidate `s`, `v`, and `V` pack/unpack values.

State and persistence behavior: in-memory stream state only; stream position and bytes are the persistence model under test.

Dependencies/integration points: these primitives underpin bup protocol and on-disk/in-stream compact encodings. Tests also enforce error wording for invalid formats and EOF contexts.

Risks and test signals: huge integer values test arbitrary precision behavior. Signals are exact round-trip lists, `None` on clean EOF, `EOFError` on truncation, and `ValueError` messages for format misuse.
