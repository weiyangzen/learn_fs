# sources/user-network-fs/s3fs-fuse/src/s3fs_global.cpp

Purpose: defines shared process-wide configuration and request counters declared elsewhere, including foreground/logging flags, multipart/path/XML/security flags, endpoint settings, program/instance names, and atomic S3 operation counters.

Important APIs and types: no functions are defined. Exported globals include `foreground`, `nomultipart`, `pathrequeststyle`, `noxmlns`, `insecure_logging`, `program_name`, `service_path`, `s3host`, `region`, `cipher_suites`, `instance_name`, and atomics such as `num_requests_head_object`, `num_requests_put_object`, and multipart counters.

Control flow: these variables are initialized at process start with defaults and then mutated by option parsing and runtime request code. Logging, credentials, XML parsing, and curl behavior read these globals directly.

State and persistence: all state is in process memory. Request counters are atomic for concurrent request updates; configuration strings and bools are not atomic and are expected to settle during initialization.

Dependencies and integration points: includes `common.h`, which likely declares these externs and their types. Integrated broadly with logger, credential checks, XML namespace behavior, curl request construction, metrics, and user-facing launch/version behavior.

Risks: global mutable state makes test isolation and multi-mount-in-one-process scenarios fragile. Non-atomic configuration reads are only safe if mutation is limited to startup. `insecure_logging` affects secret masking throughout the process.

Test signals: startup default tests, option parsing tests that validate global mutation, concurrent request tests for atomic counters, and regression tests ensuring secret masking follows `insecure_logging`.
