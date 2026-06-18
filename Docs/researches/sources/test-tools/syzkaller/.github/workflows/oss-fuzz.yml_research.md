<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/oss-fuzz.yml -->
# sources/test-tools/syzkaller/.github/workflows/oss-fuzz.yml research

Purpose: CI fuzzing workflow that builds and runs syzkaller fuzzers through OSS-Fuzz CIFuzz on pull requests.

Important APIs, types, and functions: uses `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master`, `run_fuzzers@master`, artifact upload on failure, and CodeQL SARIF upload.

Control flow: PRs run the build-fuzzers step, then run fuzzers for 300 seconds with Go language settings and SARIF output. If build succeeded and fuzzing fails, artifacts under `./out/artifacts` are uploaded. SARIF upload runs whenever the build step succeeded.

State and persistence: fuzz build outputs, crash artifacts, and SARIF results are job-local until uploaded as GitHub artifacts/security results.

Dependencies and integration: integrates with OSS-Fuzz project `syzkaller`, GitHub artifact storage, and CodeQL SARIF ingestion.

Risks: actions are referenced by mutable tags (`master`, `v4`, `v2`) rather than full SHAs, unlike the main CI workflow. A 300-second fuzz window is good for regression smoke testing but not deep fuzzing.

Test signals: successful fuzzer build, five-minute CIFuzz execution, uploaded crash artifacts on failure, and SARIF results visible in GitHub code scanning.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/.github/workflows/oss-fuzz.yml -->
