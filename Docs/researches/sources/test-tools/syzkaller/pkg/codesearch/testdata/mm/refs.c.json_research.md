# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/refs.c.json

Purpose: Golden codesearch output for nested fixture `mm/refs.c`.

Important APIs/types/functions: Contains definition `ref_in_mm` with body range `mm/refs.c:3-6` and one `calls` reference to function `refs2` on line 5.

Control flow: Static JSON only.

State and persistence behavior: Persisted expected entity/reference data for tests.

Dependencies/integration points: Loaded and merged into the test `Database`, then used by reference query fixtures.

Risks: Path normalization must keep the `mm/` prefix; otherwise reference source filtering can break.

Test signals: Confirms nested source path handling and references to entities defined in another file.
