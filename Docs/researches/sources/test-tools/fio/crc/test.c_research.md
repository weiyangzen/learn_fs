# sources/test-tools/fio/crc/test.c

Purpose: Implements `fio_crctest()`, fio's checksum/hash throughput benchmark for built-in CRC, cryptographic hash, and non-cryptographic hash implementations.

Important APIs/functions: Defines `struct test_type` with name, selection mask, benchmark function, and accumulator. Benchmark functions include `t_md5`, `t_crc64`, `t_crc32`, `t_crc32c`, `t_crc16`, `t_crc7`, `t_sha1`, `t_sha256`, `t_sha512`, `t_xxhash`, `t_murmur3`, `t_jhash`, `t_fnv`, and SHA3 variants. `get_test_mask()` parses comma-separated names. `list_types()` prints available algorithms. `fio_crctest()` is the public entry point.

Control flow: `fio_crctest()` probes accelerated CRC32C implementations, derives a mask from the requested type or selects all, allocates a 128 KiB buffer, fills it with deterministic random data, warms the CPU/data path on the first selected test, then times each selected function over 2048 chunks and prints MiB/s. Each function loops over `NR_CHUNKS`; streaming hashes use their context APIs while simple CRC/hash functions accumulate a result to discourage optimization.

State/persistence: Uses stack contexts and one heap buffer. `struct test_type.output` persists across runs in the static table and can accumulate if `fio_crctest()` is invoked more than once in-process.

Dependencies/integration: Pulls fio time utilities, random buffer generation, and every local checksum header. Integrated through the fio command path that exposes CRC test/list behavior.

Risks: Several streaming hash benchmark loops initialize/finalize outside or inside loops inconsistently; this is a throughput exerciser, not a digest correctness test. `malloc(CHUNK)` is not checked before filling. `get_test_mask()` ignores unknown comma elements unless the aggregate mask is zero. Static `output` is not reset per invocation.

Test signals: Expected signals are successful listing, nonzero throughput for every algorithm, and no crashes under ASAN/UBSAN. Digest correctness needs separate known-vector tests.
