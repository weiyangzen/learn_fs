# sources/storage-engines/wiredtiger/test/suite/test_dump01.py

Purpose: tests `wt dump -px`, the pretty-hex mode that prints keys in pretty form and values in hex form.

Important APIs and control flow: creates `table:test_dump` with integer keys and byte-array values. `get_bytes` generates deterministic binary values with a trailing null. The test writes values, runs `wt dump -x`, `wt dump -p`, and `wt dump -px`, then compares outputs line by line.

State and persistence: dumped output files are the primary artifacts. Table data includes bytes that require escaping/hex encoding.

Dependencies and integration: uses `suite_subprocess`, external `wt dump`, and file reads.

Risks and test signals: header lines must match pretty output except `Format=print hex`, data start must align, keys must match pretty output, and values must match hex output. It catches formatting regressions in utility output.
