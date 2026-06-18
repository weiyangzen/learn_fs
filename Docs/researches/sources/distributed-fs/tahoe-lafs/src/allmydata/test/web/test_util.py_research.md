# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/test_util.py

## Purpose
This module tests small formatting and argument-parsing helpers in Tahoe web modules. It focuses on replace semantics, time/rate/size abbreviation, rate computation, and plural suffix selection.

## Important APIs, Types, And Functions
`Util` tests `common.parse_replace_arg`, `common.abbreviate_time`, `common.compute_rate`, `common.abbreviate_rate`, `common.abbreviate_size`, and `status.plural`. It uses `ONLY_FILES`, `WebError`, `ShouldFailMixin`, and `ReallyEqualMixin`.

## Control Flow
`parse_replace_arg` maps byte strings for `true`, `false`, and `only-files` to `True`, `False`, and `ONLY_FILES`, while malformed input raises `WebError`. Abbreviation tests check boundary formatting for seconds, milliseconds, microseconds, bytes, kilobytes, megabytes, and gigabytes. `compute_rate` returns `None` for missing or zero time inputs, calculates bytes/sec for valid inputs, and asserts on negative values. Plural tests compose strings with zero, one, and multiple items.

## State And Persistence
There is no mutable state or persistence. All tests are pure helper-function assertions.

## Dependencies And Integration Points
The module integrates `allmydata.web.common`, `allmydata.web.status`, and `allmydata.dirnode.ONLY_FILES`. These helpers feed user-visible WUI and status text in other web resources.

## Risks And Test Signals
Signals include stable human-readable formatting, input validation for replace behavior, division-by-zero avoidance, and grammar for singular/plural labels. Risks are mostly compatibility-related: changing formatting precision or units will break tests and may alter user-visible output.
