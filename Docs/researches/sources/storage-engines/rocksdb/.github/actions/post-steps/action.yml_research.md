<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/post-steps/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/post-steps/action.yml

Purpose: Shared post-job artifact collection for RocksDB CI.

Important APIs/types/functions: input `artifact-prefix`; uploads test results, `LOG`, failure logs copied from `t/*`, and `core.*` dumps with `actions/upload-artifact@v4.0.0`.

Control flow: normal uploads run after jobs; failure-log copy runs only on failure; core dump upload ignores missing files. Callers often wrap this action at the end of build/test jobs.

State and persistence behavior: reads workspace/test temp files and persists them as GitHub artifacts. It creates `${{ runner.temp }}/failure-test-logs` on failing runs.

Dependencies and integration points: used broadly by PR, nightly, weekly, macOS, Linux, ARM, and Folly jobs. Relies on `pre-steps` setting `GTEST_OUTPUT` into runner temp.

Risks: uploading `LOG` without `if-no-files-found` may warn/fail depending on action defaults if the file is absent. Copying `t/*` can be large on broad failures. Artifact names need unique prefixes for matrix jobs.

Test signals: artifact availability in failed/successful CI runs and lack of post-step masking failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/post-steps/action.yml -->
