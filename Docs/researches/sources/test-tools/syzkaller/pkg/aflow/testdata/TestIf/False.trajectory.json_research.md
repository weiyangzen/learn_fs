# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/False.trajectory.json

Purpose: minimal golden trajectory for a statically false/no-op conditional path.

Important structure: only 2 spans, flow start and flow finish. Final result is `{"Done":""}`.

Control flow: no `If` wrapper or body action appears, indicating the tested construction optimized or bypassed execution for this false case.

State and persistence: persistent golden fixture with only flow-level data.

Dependencies and integration: consumed by `If` tests to validate the simplest false condition path.

Risks and test signals: detects accidental introduction of wrapper/action spans for this no-op false path, or failure to preserve zero-valued output fields.
