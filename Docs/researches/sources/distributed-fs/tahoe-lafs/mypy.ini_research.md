# sources/distributed-fs/tahoe-lafs/mypy.ini

## Purpose

This is Tahoe-LAFS's mypy configuration. It sets a permissive global baseline with selected strictness flags and then enables a much stricter profile for a few typed modules.

## Important APIs, Types, And Functions

The `[mypy]` section enables `ignore_missing_imports`, the `mypy_zope` plugin, pretty output, column numbers, error codes, no implicit optionals, redundant-cast warnings, and strict equality. A targeted module section applies strict checks such as `disallow_untyped_defs`, `check_untyped_defs`, `warn_return_any`, `no_implicit_reexport`, and `strict_concatenate` to `allmydata.test.cli.wormholetesting`, `allmydata.listeners`, and `allmydata.test.test_connection_status`.

## Control Flow

There is no runtime control flow. Mypy reads this file to decide which imports to ignore and which static-analysis checks to enforce per module pattern.

## State And Persistence

The file is static configuration. Its state is persisted in the repository and affects developer/CI type-check behavior, not Tahoe node runtime behavior.

## Dependencies And Integration Points

It integrates with mypy and `mypy_zope:plugin`, which is important for Zope interface-heavy code. The strict target list signals incremental typing adoption.

## Risks

`ignore_missing_imports = True` can hide missing or untyped dependency problems. The global baseline is not fully strict, so typed and untyped regions can diverge. The typo-like spacing in `warn_unused_configs =True` is accepted by config parsing but should be kept consistent if edited.

## Test Signals

Run mypy with this config and confirm the targeted modules still pass strict checks. Adding a new strict module should produce expected failures for untyped definitions and imports.
