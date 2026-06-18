# sources/test-tools/syzkaller/pkg/aflow/testdata/TestFlowConsts.trajectory.json

Purpose: golden trajectory for a flow that consumes constant-provided input.

Important structure: 4 spans total: flow start/finish and `input-consumer` action start/finish.

Control flow: the action `input-consumer` executes successfully inside flow `test`; final flow result is an empty object. The short fixture verifies const injection without additional branching, loops, or LLM calls.

State and persistence: stores only deterministic span timing and empty final results. The constants themselves are visible through the action args during execution, but the final fixture records no durable application state.

Dependencies and integration: consumed by a flow const test elsewhere in the aflow package via `testFlow`.

Risks and test signals: detects regressions where consts are not available to action argument conversion, or where no-output actions stop producing an empty final result map.
