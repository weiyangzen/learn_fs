# sources/sync-backup/borg/src/borg/testsuite/helpers/yes_no_test.py

Purpose: tests interactive yes/no prompting, environment overrides, defaults, retry behavior, custom truthy/falsy sets, and user-facing output.

Important APIs and control flow: tests feed `FakeInputs` containing `TRUISH`, `FALSISH`, `DEFAULTISH`, invalid inputs, and custom values into `yes`. Environment override tests set a variable and bypass input. Defaults are checked for blank/defaultish/no-input cases, with `default=None` raising `ValueError`. Retry and no-retry paths verify how invalid inputs are handled. Output tests assert stderr contains intro, retry, true/false, and environment override messages while stdout remains empty.

State and persistence: mutates environment variables and consumes `FakeInputs`; no disk state.

Dependencies and integration points: depends on `helpers.yes_no.yes`, constants `TRUISH`, `FALSISH`, `DEFAULTISH`, and testsuite `FakeInputs`. It supports CLI confirmations and noninteractive env overrides.

Risks: default handling can silently choose actions when input is exhausted. Environment override values are printed, so output should avoid leaking unrelated secrets.

Test signals: boolean decisions, expected exceptions, and exact stderr inclusion/exclusion.
