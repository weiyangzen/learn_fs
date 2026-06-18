# sources/storage-engines/tikv/tests/integrations/coprocessor/test_analyze.rs

## sources/storage-engines/tikv/tests/integrations/coprocessor/test_analyze.rs

Purpose: integration tests for TiKV coprocessor analyze requests over table and index data, including lock behavior and full sampling modes.

Important APIs: coprocessor `Request`, `KeyRange`, `Context`, `IsolationLevel`, tipb `AnalyzeReq`, `AnalyzeColumnsReq`, `AnalyzeIndexReq`, `AnalyzeColumnsResp`, `AnalyzeIndexResp`, `AnalyzeColumnGroup`, `AnalyzeType`, and helpers `new_analyze_*`.

Control flow: request builders encode analyze protobufs, set ranges from `ProductTable`, and assign `REQ_TYPE_ANALYZE`. Tests initialize product data, issue analyze column/index requests, deserialize responses, and assert histogram bucket counts, NDV, null counts, CM sketch rows, total sizes, TopN counts, sampling row collectors, and invalid-range errors. Lock tests run under SI and RC: SI returns lock info with empty data, while RC bypasses locks and returns empty statistics.

State and persistence: test data is committed or left locked in test storage through `init_data_with_commit`; responses are in-memory protobufs. No external files are written.

Dependencies and integration points: TiDB protobuf stats formats, MVCC isolation semantics, test table metadata, and coprocessor endpoint request handling. Risks include statistical algorithm changes, nondeterministic sampling if not controlled by fixture size, and lock behavior differences. Test signals are exact stats-field assertions and error/lock presence.
