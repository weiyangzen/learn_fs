# sources/test-tools/syzkaller/pkg/codesearch/testdata/mm/refs.c

Purpose: Small nested-directory C fixture for cross-directory reference search.

Important APIs/types/functions: Declares `int refs2();` and defines `ref_in_mm`, which calls `refs2`.

Control flow: `ref_in_mm` performs a single call to an externally defined `refs2`.

State and persistence behavior: No runtime state. Expected extracted state lives in `mm/refs.c.json`.

Dependencies/integration points: Tests `FindReferences` with source prefixes and nested paths such as `mm/refs.c`.

Risks: The declaration signature differs from the full definition in root `refs.c`, which is useful for extraction but can expose compiler warning sensitivity.

Test signals: Golden JSON records one function definition with a call reference to `refs2`.
