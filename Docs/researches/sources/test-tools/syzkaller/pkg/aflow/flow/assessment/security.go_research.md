# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/security.go

## Purpose

`security.go` registers the security assessment workflow, which evaluates exploitability and reachable attack surfaces for syzkaller kernel bugs.

## Important APIs, Types, and Functions

`assessmentSecurityInputs` includes crash report, syz/C repros, and kernel environment fields. `securityOutputs` defines structured booleans for exploitability, denial-of-service, unprivileged/user namespace access, VM guest/host triggers, network/remote/peripheral/filesystem triggers. The init function registers `ai.WorkflowAssessmentSecurity` producing `ai.AssessmentSecurityOutputs`.

## Control Flow

The pipeline first creates a simplified C repro, checks out/builds the kernel, prepares the code index, runs an expensive-model `LLMAgent` named `expert` with security instruction/prompt and code access tools, and wraps its raw explanation. The prompt includes crash report and conditionally includes the simplified C repro.

## State and Persistence Behavior

Kernel source/builds are cached. LLM structured booleans and formatted explanation become persisted dashboard output fields. The simplified C repro is transient workflow state.

## Dependencies and Integration Points

It integrates `actionsyzlang.CreateSimplifiedCRepro`, kernel build/index actions, common prompt loading, and code access tools. The output schema matches `ai.AssessmentSecurityOutputs`, which is used by dashboard predicates.

## Risks and Edge Cases

Security labels are high-impact and LLM-derived, so prompt/tool reliability matters. The prompt text has a typo (`followint`) but behavior is unaffected. If `ReproSyz` is absent, the simplified C repro may be just the provided C repro or empty. Build failures block the assessment.

## Test Signals

Registration tests verify dataflow and schema matching. There are no ground-truth exploitability classification tests in this set.
