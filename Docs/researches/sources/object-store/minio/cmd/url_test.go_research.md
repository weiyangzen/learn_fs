# sources/object-store/minio/cmd/url_test.go

Contains allocation/performance benchmarks for query parameter access. `BenchmarkURLQueryForm` parses the request form once and reads `req.Form.Get("uploadId")` in parallel; `BenchmarkURLQuery` repeatedly calls `req.URL.Query().Get("uploadId")`.

There is no persistent state or correctness assertion. The file is useful for detecting allocation regressions in hot request parsing choices when benchmarks are run.
