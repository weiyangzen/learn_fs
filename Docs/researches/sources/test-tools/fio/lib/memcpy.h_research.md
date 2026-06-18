# sources/test-tools/fio/lib/memcpy.h

Purpose: declares the memory-copy benchmark entry point.

Important APIs/functions: `fio_memcpy_test(const char *type)`, where `type` may be null for all tests, `help`/`list`, or a comma-separated set of copy method names.

Control flow/state: no header state; callers run the benchmark and receive process-style success/failure integer status.

Dependencies/integration: implementation depends on fio timing and RNG, but the header is intentionally minimal.

Risks/test signals: this API prints directly and is unsuitable for library-style quiet use. Tests should cover unknown type handling and help/list behavior.
