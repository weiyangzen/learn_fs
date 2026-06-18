# sources/storage-engines/wiredtiger/test/suite/test_checkpoint15.py

Purpose: verifies each checkpoint carries independent timestamp metadata by writing multiple checkpoints at different stable/oldest times and reading all accessible timestamps.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, `session.checkpoint` named/unnamed helper `do_checkpoint`, `checkpoint_read_timestamp`, and `wiredtiger.WiredTigerError` for before-oldest reads.

Control flow: set oldest/stable to 5, write timestamp-10 data and checkpoint, write timestamp-20 data and create first checkpoint, write timestamp-30 data, set oldest 15 and create second checkpoint, write timestamp-40 data, set oldest 25 and create third checkpoint. Reads verify first checkpoint can read timestamp 10 and 20/default, second rejects 10 but reads 20 and 30/default, and third rejects 10/20 but reads 30 and 40/default.

State/persistence behavior: checkpoint metadata stores both the stable content and the oldest timestamp boundary at creation time. Later oldest advancement must not rewrite older checkpoint metadata incorrectly.

Dependencies/integration: named/unnamed checkpoint availability, timestamped checkpoint reads, precise/fuzzy modes, and row/column formats.

Risks/test signals: unnamed checkpoints are only used for the most recent checkpoint because older unnamed checkpoints cannot be reopened by name.
