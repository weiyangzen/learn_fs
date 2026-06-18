# sources/test-tools/syzkaller/pkg/aflow/runner_test.go

Purpose: central test harness for executing aflow workflows and comparing produced trajectories and LLM requests with golden files.

Important APIs/functions: `testFlow[Inputs, Outputs]` registers a test flow, installs a stub `generateContent`, executes the flow, serializes spans and LLM requests through JSON, optionally updates golden files via `-update`, and compares results. `testRegistrationError` asserts registration failures. `setupDefaults` fills defaults for `LLMAgent`, `pipeline`, `If`, `DoWhile`, and `ForEach`.

Control flow: the LLM stub records model/config/request snapshots, consumes provided replies, supports callback replies, and converts `*genai.Part` or `[]*genai.Part` into `GenerateContentResponse`. After `Flow.Execute`, the harness compares either output maps or expected error strings, then checks `testdata/<TestName>.trajectory.json` and optional `.llm.json`.

State and persistence: test state is held in local slices `requests` and `spans`, a temporary workdir, and a test cache. Persistent golden files are read or rewritten only when `-update` is supplied.

Dependencies and integration: depends on `context`, `encoding/json`, `flag`, `os`, `filepath`, `reflect`, `slices`, `time`, syzkaller `trajectory`/`osutil`, testify `require`, and `genai`. It is the integration point for most aflow unit tests that need deterministic time and LLM behavior.

Risks and test signals: exact golden matching is high signal but brittle when span schemas, timestamps, config serialization, or default prompts change. The `lastConfig` elision logic means `.llm.json` files intentionally omit repeated configs unless they change.
