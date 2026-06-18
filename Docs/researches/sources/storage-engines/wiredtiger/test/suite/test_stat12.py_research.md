<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat12.py

Purpose: validates eviction trigger and application-thread fill-ratio statistics exist, increment under cache pressure, and are bucketed by actual cache fill ratio.

Important APIs/types/functions: `test_stat12` and `test_stat12_fill_ratio_bucketing` use small-cache connection configs, eviction target/trigger settings, `wiredtiger.stat.conn.cache_eviction_trigger_*`, fill-ratio bucket stats, helper `populate_data`, and timed polling.

Control flow: existence tests simply read trigger and fill-ratio stats. Increment tests create a table, insert large values to fill a 1MB cache, checkpoint, dirty many records, read clean pages, then poll stats until eviction trigger and fill-ratio counters increase. Bucketing test configures all triggers above 50%, writes and dirties enough data, polls upper buckets, and asserts lower buckets stay zero.

State and persistence behavior: state is runtime cache pressure and dirty/update thresholds. Checkpoint separates clean from dirty phases, while polling allows eviction threads to process.

Dependencies/integration points: covers eviction configuration, app-thread eviction accounting, connection stats, dirty/update triggers, and floating-point fill-ratio computation. Risks include timing sensitivity under slow machines; signals are nonzero trigger/fill counters and correct bucket distribution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat12.py -->
