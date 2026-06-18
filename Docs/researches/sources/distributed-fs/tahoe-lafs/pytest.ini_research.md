# sources/distributed-fs/tahoe-lafs/pytest.ini

## Purpose

This file declares pytest metadata for the Tahoe-LAFS test suite.

## Important APIs, Types, And Functions

The only configured marker is `slow`, described as tests not run by default and enabled with `--runslow`.

## Control Flow

Pytest reads this file during collection to register the marker and avoid unknown-marker warnings.

## State And Persistence

The file is static test configuration with no runtime state.

## Dependencies And Integration Points

It integrates with pytest and any local conftest/plugin logic that interprets `--runslow`.

## Risks

The marker description implies custom `--runslow` handling elsewhere; without that hook the marker alone does not skip slow tests. Adding markers in tests without updating this file can produce warnings or strict-marker failures.

## Test Signals

Run `pytest --markers` and confirm `slow` appears. Run normal pytest and `pytest --runslow` in the repository's supported test environment to confirm intended selection behavior.
