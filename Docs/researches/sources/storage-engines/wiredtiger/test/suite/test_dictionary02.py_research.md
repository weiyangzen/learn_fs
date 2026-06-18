# sources/storage-engines/wiredtiger/test/suite/test_dictionary02.py

Purpose: verifies dictionary reuse when repeated cells also carry run-length encoding information, especially for VLCS.

Important APIs and control flow: row and variable-column scenarios create a file with dictionary compression. The test pins oldest and stable timestamps at 1, writes two unique large values, then writes keys 3 through 9 with the first value. After checkpoint, it reads `stat.dsrc.rec_dictionary`.

State and persistence: checkpointed reconciliation creates the dictionary entries and RLE encoding. Timestamp pinning prevents global visibility from simplifying the cells unexpectedly.

Dependencies and integration: uses `simple_key`, `make_scenarios`, and `wiredtiger.stat`.

Risks and test signals: expected dictionary counts differ by format: row-store writes seven reused cells, while VLCS RLE collapses them to one reused cell. This catches interactions between dictionary and RLE encoding.
