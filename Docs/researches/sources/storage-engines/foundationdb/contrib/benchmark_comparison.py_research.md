# sources/storage-engines/foundationdb/contrib/benchmark_comparison.py

Purpose: runs `flow_bench` benchmark filters and prints a formatted actor-vs-coroutine performance comparison report for delay, net2, and callback benchmark families.

Important APIs/functions: `geomean`, `get_benchmark_data`, and `main`.

Control flow: `get_benchmark_data` invokes `./bin/flow_bench --benchmark_filter=... --benchmark_format=json` with hard-coded cwd `/root/build_output`. `main` pairs actor and coroutine benchmarks by scale/template size, computes relative real-time and CPU changes, prints rows, and prints section geomeans.

State and persistence: no files; subprocess output parsed as JSON and report printed to stdout.

Dependencies and integration: requires a build tree containing `bin/flow_bench` and Google Benchmark JSON format.

Risks and test signals: hard-coded cwd limits portability; geomean uses absolute changes and loses improvement/degradation sign semantics for mixed sets; missing benchmarks are silently skipped. Test with mocked JSON, missing executable, zero old timings, and each benchmark family.
