# sources/storage-engines/rocksdb/build_tools/check-public-header.sh research

Purpose: `check-public-header.sh` is a lightweight guard for public RocksDB headers. It detects preprocessor conditionals that could create ODR violations when public headers compile differently in RocksDB and in downstream applications.

Important APIs: the script accepts header paths as command-line arguments. It has no functions; the observable contract is exit status 0 for clean input and 1 for detected issues.

Control flow: it initializes `BAD`, runs `grep -nHE '^#if' -- "$@"`, filters out known-safe or intentional patterns such as `ROCKSDB_NAMESPACE`, `ROCKSDB_ASSERT_STATUS_CHECKED`, Windows macros, `ODR-SAFE`, `__cplusplus`, and DLL export macros. If suspicious matches remain, it prints guidance and sets `BAD=1`; the final block exits nonzero when `BAD` is set.

State and persistence: there is no persistent state. It reads only the files named on the command line and writes diagnostics to stdout.

Dependencies and integration: it depends on `bash` and `grep`. It fits pre-commit, CI, or `make check` style validation for public API headers.

Risks and test signals: the grep pattern only sees lines beginning with `#if`, not all conditional forms or multi-line macros. False positives are expected and are suppressed with an `ODR-SAFE` marker after manual review. False negatives are possible for conditionals hidden behind formatting or macros. Tests should include safe and unsafe header snippets and validate the expected exit code.
