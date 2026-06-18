# sources/storage-engines/tikv/scripts/test-all

## Purpose
Broad pre-submit wrapper that runs normal tests, Linux malloc-configuration tests, and Linux binary policy checks.

## Important Commands and Control Flow
The script re-enters through `make run` unless `MAKEFILE_RUN` is set. It first runs `./scripts/test "$@"`. On Linux it exports `MALLOC_CONF=prof:true` and reruns `./scripts/test ifdef_malloc_conf "$@"`. Also on Linux, it invokes `scripts/test` with `CUSTOM_TEST_COMMAND="" EXTRA_CARGO_ARGS="" --message-format=json-render-diagnostics -q --no-run` and pipes Cargo JSON to `python3 scripts/check-bins.py --features "${TIKV_ENABLE_FEATURES}" --check-tests`.

## State, Dependencies, Integration
No custom state is persisted; Cargo artifacts and test outputs are normal. It depends on `scripts/test`, Python 3, `scripts/check-bins.py`, Linux binary tools used by that script, Cargo JSON output, and Makefile-defined `TIKV_ENABLE_FEATURES`.

## Risks and Test Signals
The Linux binary phase requires `TIKV_ENABLE_FEATURES` under `set -u`. The no-run build can be expensive, and allocator/linkage checks are skipped on non-Linux systems. Passing all phases indicates normal tests, malloc-conf-specific tests, and binary policy checks succeeded.
