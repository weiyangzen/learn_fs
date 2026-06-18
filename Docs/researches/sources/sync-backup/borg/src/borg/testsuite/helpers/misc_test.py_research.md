# sources/sync-backup/borg/src/borg/testsuite/helpers/misc_test.py

Purpose: tests miscellaneous iterator/file-wrapper helpers.

Important APIs and control flow: `ChunkIteratorFileWrapper` is read with small and large sizes over byte chunks and must report exhaustion. `chunkit` chunks iterables into fixed-size lists and remains exhausted on repeated `next`. `iter_separated` reads separated text and byte streams using newline, NUL, and multi-character separators, including trailing separators.

State and persistence: in-memory `StringIO`/`BytesIO` and iterator state only.

Dependencies and integration points: depends on `helpers.misc.ChunkIteratorFileWrapper`, `chunkit`, and `iter_separated`. These are integration helpers for command inputs, chunk streams, and separated lists.

Risks: EOF/exhaustion behavior is easy to get wrong, especially with trailing separators and bytes-versus-text streams.

Test signals: exact read fragments, chunk lists, and separated item lists.
