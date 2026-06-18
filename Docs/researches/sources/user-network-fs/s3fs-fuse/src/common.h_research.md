<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/common.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/common.h

Purpose: shared global declarations and cross-file constants/macros for the s3fs codebase. It centralizes mount/request configuration globals, request counters, multipart size constants, weak-function attributes, and clang thread-safety annotation compatibility macros.

Important APIs/types: exports constants `FIVE_GB` and `MIN_MULTIPART_SIZE`. Declares global mount/config variables such as `foreground`, `nomultipart`, `pathrequeststyle`, `noxmlns`, `insecure_logging`, `program_name`, `service_path`, `s3host`, `mount_prefix`, `region`, `cipher_suites`, and `instance_name`. Declares atomic request counters for HEAD/PUT/GET/DELETE/LIST and multipart phases. Defines `S3FS_FUNCATTR_WEAK` and thread-safety macros `GUARDED_BY`, `PT_GUARDED_BY`, `REQUIRES`, `RETURN_CAPABILITY`, `ACQUIRED_BEFORE`, `ACQUIRED_AFTER`, and `NO_THREAD_SAFETY_ANALYSIS`.

Control flow: this header contains no runtime control flow. Its compile-time flow is conditional: under clang, thread annotations expand to attributes; under other compilers, they are no-ops. The included generated `config.h` controls version and feature symbols used elsewhere.

State and persistence: no storage is defined here, but the `extern` globals are mutable process-wide state used by request construction, logging, credential/signing behavior, and statistics. Request counters are atomics, which makes increments safe across FUSE threads, but other string/bool globals rely on initialization-time mutation or external discipline.

Dependencies/integration: heavily included by cache, curl, auth, and utility code. `FIVE_GB` and `MIN_MULTIPART_SIZE` integrate with multipart upload limits. Thread annotations are consumed by headers such as `cache_node.h`, `curl.h`, and `curl_share.h` to document mutex discipline without requiring clang.

Risks: global mutable configuration makes tests and long-running process reconfiguration sensitive to initialization order and teardown leakage. The `TODO: namespace these` comment is apt: symbol collisions are possible in a large C++ codebase. Non-atomic globals read by request paths should be set before worker threads start. On non-clang compilers, thread-safety annotations disappear, so lock-contract regressions can slip through unless clang analysis is part of CI.

Test signals: build with clang thread-safety warnings enabled, verify generated `config.h` supplies expected symbols, and run integration tests that assert request counters increment under concurrent S3 operations. Configuration tests should ensure globals are initialized once before request-handling threads start.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/common.h -->
