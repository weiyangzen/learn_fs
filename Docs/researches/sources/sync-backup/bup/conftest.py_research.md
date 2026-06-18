# sources/sync-backup/bup/conftest.py

## Purpose
Pytest configuration for bup tests. It sets common environment isolation, source import path, deterministic temp directories, saved-error checks, and collection ordering.

## Important APIs, Types, and Functions
Defines hooks `pytest_runtest_makereport` and `pytest_collection_modifyitems`, helper `bup_test_sort_order`, autouse fixtures `no_lingering_errors` and `common_test_environment`, and fixture `tmpdir`.

## Control Flow
At import, it prepends `lib` to `sys.path`, sets `BUP_TEST_LEVEL`, `BUP_DIR`, and `GIT_DIR`, normalizes cwd, and creates `test/tmp`. Each test gets a temporary `HOME`, environment restoration, saved-errors clear/check before and after, and per-test temp directory cleanup or preservation on failure.

## State and Persistence Behavior
Mutates process environment and cwd during tests, creates `test/tmp/home-*` and test-specific temp dirs, and preserves failed-test homes/tmpdirs for debugging. `helpers.saved_errors` is treated as a failure ledger.

## Dependencies and Integration Points
Integrates pytest with `bup.helpers.finalized`, byte environment helpers, test ordering for slow tests, and bup's global error collection.

## Risks and Test Signals
Risks include autouse fixture masking env interactions, unsafe cleanup permissions, and reliance on `request.node.bup['call-report']`. Signals are no lingering saved errors, isolated `HOME`, restored env/TZ, and preserved artifacts only on failures.
