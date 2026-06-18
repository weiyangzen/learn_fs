# `sources/test-tools/fio/.github/workflows/cifuzz.yml`

Purpose: Runs OSS-Fuzz CIFuzz for fio on pull requests and manual dispatch.

Important jobs and settings: Single `Fuzzing` job on Ubuntu. It builds fuzzers with `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master`, runs them for 600 seconds with `run_fuzzers@master`, and uploads crash artifacts from `./out/artifacts` if fuzz execution fails after a successful build.

Control flow: Build step creates fuzzers for OSS-Fuzz project `fio`; run step executes them; upload step preserves reproducer/crash data on failure.

State and persistence: Temporary fuzz build and output directories are created on the runner. Artifact upload persists crashes for review.

Dependencies and integration: Depends on OSS-Fuzz GitHub Actions, the external fio OSS-Fuzz project definition, and GitHub artifact upload.

Risks and test signals: Actions are pinned to `master`, which can change behavior. Ten-minute fuzzing is useful for regression smoke but not exhaustive. Tests should confirm fuzz targets still build under the OSS-Fuzz configuration and that failure artifacts are collected.
