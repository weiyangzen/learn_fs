# sources/test-tools/syzkaller/pkg/aflow/flow/repro/repro.go

## Purpose

`repro.go` registers the syzkaller-program reproduction workflow. It asks an LLM to generate a syzlang reproducer for a kernel crash, formats it, executes it in VMs, and reports whether it reproduced the original title.

## Important APIs, Types, and Functions

`ReproInputs` carries agent, target, bug, kernel, image/VM, syzkaller, and strace fields. The init function registers `ai.WorkflowRepro` producing `ai.ReproOutputs`. Consts include syzkaller commit, syzlang docs, syscall description file list, empty `ReproC`, and `NeedStrace=false`. The inline `compare` action outputs `Reproduced`.

## Control Flow

The pipeline checks out/builds the kernel, prepares code search, runs an expensive-model `crash-repro-finder` LLM with code tools plus syzlang description/reproduce/coverage tools, requests `ReproOpts` and `CandidateReproSyz`, formats the candidate strictly via `actionsyzlang.Format`, reproduces the crash via `crash.Reproduce`, and compares the original `BugTitle` to `ReproducedBugTitle`.

## State and Persistence Behavior

Kernel artifacts and reproduction executions are cached by underlying actions. The generated syz program, options, syzkaller commit, crash reports, and reproduced flag become persisted output fields.

## Dependencies and Integration Points

It integrates syzkaller docs, program revision metadata, kernel actions, code search, syzlang tools, crash reproduction, and aflow LLM structured outputs. It is a dashboard workflow for generating syz repros.

## Risks and Edge Cases

Title equality is a strict reproduced check even when crashes may be equivalent under a different title. The LLM may produce invalid syzlang, caught by strict formatting. `ReproC` is set to empty only to satisfy `crash.Reproduce` inputs. The workflow builds/indexes the kernel before generation, increasing cost but enabling code-aware tools.

## Test Signals

Registration tests validate dataflow. Full behavior depends on LLM stubs or integration runs with VM images and syzkaller tools.
