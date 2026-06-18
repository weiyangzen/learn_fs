# sources/storage-engines/tikv/tests/integrations/resource_metering/test_read_keys.rs

Purpose: verifies `read_keys` resource metering for point/scan KV reads and coprocessor reads. Both top-level tests are ignored as unstable but preserve expected integration behavior.

Important APIs and functions: `test_read_keys`, `new_cluster`, `must_recv_read_keys`, `recv_read_keys`, `test_read_keys_coprocessor`, `init_coprocessor_with_data`, `handle_select`, and `MockDataSink` implementing `resource_metering::DataSink`.

Control flow: the KV test starts a mock receiver, configures a raftstore cluster with short precision/report intervals, writes ten keys, warms up a get, then expects point get = 1 read key, scan limit 5 = 5, and scan all = 10. The coprocessor test initializes recorder/reporter directly, registers `MockDataSink`, loads four rows, executes a tagged DAG request once to register threads, clears output, executes again, and expects four read keys.

State and persistence: persists MVCC rows in raftstore or test Rocks storage; accounting is batched in recorder/reporter workers and observed via receiver batches or mock data sink channel.

Dependencies and integration: TiKV gRPC KV APIs, raftstore clusters, resource metering receiver protocol, coprocessor endpoint, protobuf decoding, and `ResourceTagFactory`.

Risks: both tests are `#[ignore = "the case is unstable, ref #11765"]`; thread registration, report timing, and timeouts are known flaky areas.

Test signals: when manually passing, confirms point get, scan, and DAG select contribute expected read-key counts to resource usage records.
