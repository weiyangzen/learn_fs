# sources/user-network-fs/samba/source4/torture/gpo/gpo.c

## Purpose
This file is the smbtorture registration entry point for Group Policy tests. It creates the top-level `gpo` suite, attaches the apply sub-suite, and registers it with the torture framework.

## Important APIs, Types, and Functions
The sole function is `NTSTATUS torture_gpo_init(TALLOC_CTX *ctx)`. It calls `torture_suite_create(ctx, "gpo")`, adds `gpo_apply_suite(suite)` through `torture_suite_add_suite()`, sets a description, registers the suite with `torture_register_suite()`, and returns `NT_STATUS_OK`.

## Control Flow
When the `TORTURE_GPO` module is loaded, the build-declared init function `torture_gpo_init` runs. It constructs the suite hierarchy and exposes the apply tests to smbtorture discovery.

## State and Persistence Behavior
The file has no persistent runtime state beyond allocating suite metadata under the supplied talloc context. It does not execute tests directly.

## Dependencies and Integration Points
It depends on `torture/smbtorture.h` and generated/local `torture/gpo/proto.h`. Its direct integration point is `gpo_apply_suite()` from `apply.c`; its external integration point is the `TORTURE_GPO` build module's `init_function`.

## Risks
The file is small but critical for discoverability: if the suite name, init function, or sub-suite call drifts from `wscript_build`, GPO tests may compile but not appear in smbtorture. There is no local validation of `gpo_apply_suite()` returning a non-null suite.

## Test Signals
The signal is suite registration: smbtorture should list a `gpo` suite with an `apply` child containing the GPO parameter test.
