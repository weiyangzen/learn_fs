# sources/user-network-fs/samba/source4/torture/raw/raw.c

## Purpose
This file is the registration hub for the `raw` smbtorture suite. It does not implement protocol checks itself; instead, `torture_raw_init()` creates the suite, attaches all raw SMB subtests and nested suites, sets a description, and registers the suite with the torture framework.

## Important APIs, Types, And Functions
The only function is `torture_raw_init(TALLOC_CTX *ctx)`. It uses `torture_suite_create()`, `torture_suite_add_simple_test()`, `torture_suite_add_1smb_test()`, `torture_suite_add_suite()`, and `torture_register_suite()`. It references many externally implemented entry points from `torture/raw/proto.h`.

## Control Flow
Initialization creates a suite named `raw`, adds benchmarks, single-connection tests, grouped nested suites, Samba3 compatibility tests, and scan tests, then assigns `"Tests for the raw SMB interface"` as the description. It returns `NT_STATUS_OK` after successful registration. There is no conditional registration logic in this file.

## State And Persistence Behavior
The file only mutates in-memory torture registration state under the provided talloc context. It creates no SMB connections, files, or persistent artifacts directly. Runtime state and cleanup belong to the individual tests it registers.

## Dependencies And Integration Points
This file is the integration point that exposes raw SMB tests to smbtorture. It depends on `torture/smbtorture.h`, `torture/util.h`, `libcli/raw/libcliraw.h`, and generated raw torture prototypes. The order and names here define how users invoke tests such as `RAW-QFSINFO`, `RAW-READ`, `RAW-RENAME`, `RAW-SAMBA3HIDE`, and others through the test runner.

## Risks And Edge Cases
Because this is a registry, stale prototypes or renamed tests cause build failures or missing runtime coverage. Adding a test in its implementation file is not enough unless it is registered here or inside a nested suite already registered here. The explicit test names are user-facing and may be consumed by automation.

## Test Signals
There are no direct protocol assertions. The signal is structural: the raw suite appears in smbtorture with all expected children, and `torture_raw_init()` returns `NT_STATUS_OK`. Missing registrations show up as absent test names rather than failed SMB operations.
