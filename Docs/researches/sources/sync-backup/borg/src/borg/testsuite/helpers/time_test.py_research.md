# sources/sync-backup/borg/src/borg/testsuite/helpers/time_test.py

Purpose: tests timestamp clamping helpers for nanoseconds and seconds on 32-bit and wider platforms.

Important APIs and control flow: `utcfromtimestamp` wraps `datetime.fromtimestamp(..., timezone.utc)` and strips tzinfo. `test_safe_timestamps` branches on `SUPPORT_32BIT_PLATFORMS`; both branches clamp negative values to zero, clamp huge nanoseconds into signed int64, and ensure huge seconds do not overflow datetime. The 32-bit branch clamps seconds to int32, while the wider branch clamps seconds so nanosecond conversion still fits int64.

State and persistence: pure numeric/date operations.

Dependencies and integration points: depends on `helpers.time.safe_ns`, `safe_s`, and `SUPPORT_32BIT_PLATFORMS`. These functions protect archive item timestamps and platform conversion code.

Risks: platform datetime ranges vary, and the tests intentionally use extremely large values that would otherwise hit Python's Y10K/overflow limits.

Test signals: no overflow after clamping, negative-to-zero behavior, and post-2038/post-2262 sanity thresholds.
