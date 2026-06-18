<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen_disagg.yml -->
# sources/storage-engines/wiredtiger/test/evergreen_disagg.yml

Purpose: standalone Evergreen project config for WiredTiger disaggregated-storage stress tests marked failure-expected. It duplicates base Evergreen setup/build/artifact functions needed by the `wiredtiger-disagg` project.

Important structures: global `pre`, `post`, `timeout`, and `exec_timeout_secs` define cleanup, environment setup, stacktrace/stat/artifact upload, hang analysis, and cleanup. Functions cover project checkout, GitHub token for automation scripts, configure/build WiredTiger, artifact fetch/upload, disagg format tests, and timestamp-abort disagg tests. Variables define reusable task anchors for disagg switch/multi/multi-validation/delete-enabled variants, timestamp abort, built-in extension flags, and ASan clang flags.

Control flow: `compile` checks out and builds WiredTiger. Stress tasks depend on compile, fetch artifacts, prepare test environment with sanitizer/TCMalloc/extension settings, then run format or timestamp abort loops with disagg-specific args. Build variants schedule normal ARM64 stress with TCMalloc and ASan stress without TCMalloc.

State and persistence: declarative config controls artifact tarballs, S3 uploads, core files, stats, and WT test homes at runtime.

Dependencies and integration: relies on Evergreen expansions, AWS credentials, MongoDB toolchain, CMake presets, tcmalloc script, and WiredTiger disagg test flags.

Risks and test signals: duplicated base config can drift from `test/evergreen.yml`. Many tasks are explicitly failure-expected due to open WT tickets. Sanitizer and TCMalloc are mutually guarded. Post functions preserve diagnostics even on failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen_disagg.yml -->
