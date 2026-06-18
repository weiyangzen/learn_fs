# sources/storage-engines/wiredtiger/test/suite/test_dictionary01.py

Purpose: smoke test that dictionary compression is effective for repeated values in row-store and variable-length column-store files.

Important APIs and control flow: scenarios use `key_format=S` and `key_format=r`. The test creates `file:test_dictionary01` with `leaf_page_max=64K,dictionary=100,value_format=S`, inserts 25000 alternating repeated values using `simple_key`, checkpoints, and reads `stat.dsrc.rec_dictionary`.

State and persistence: checkpoint forces reconciliation, where dictionary compression decisions are made. The statistic records dictionary reuse during reconciliation.

Dependencies and integration: uses `make_scenarios`, `simple_key`, `wiredtiger.stat`, and `statistics:<uri>`.

Risks and test signals: alternating values prevent VLCS run-length encoding from collapsing the whole workload. The assertion expects dictionary reuse for almost all entries (`> nentries - 100`), catching dictionary compression regressions.
