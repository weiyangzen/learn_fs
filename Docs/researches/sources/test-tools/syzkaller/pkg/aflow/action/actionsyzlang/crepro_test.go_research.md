# sources/test-tools/syzkaller/pkg/aflow/action/actionsyzlang/crepro_test.go

## Purpose

`crepro_test.go` verifies syz-to-C conversion and large-data truncation for the `CreateSimplifiedCRepro` implementation.

## Important APIs, Types, and Functions

The tests call unexported `createCRepro` directly with `createCReproArgs` and call `truncateLargeData` directly. `TestSyzlangToC`, `TestSyzlangToC_Invalid`, `TestSyzlangToC_Empty`, and `TestTruncateLargeData` are the main test cases.

## Control Flow

The conversion test iterates amd64 and arm64, skips unsupported host/compiler combinations using `targets.Get` and `runtime.GOOS`, builds a valid syz program, and asserts the generated C contains `int main`. The invalid test feeds an unknown syscall and checks the wrapped deserialization error. The truncation test compares exact output for multiline adjacent string literals, one long single-line literal, and a short literal that must remain unchanged.

## State and Persistence Behavior

The tests do not create aflow contexts or persistent cache state. They depend on target metadata and host build support for some architectures, and use `t.Skipf` rather than failing when the host cannot build.

## Dependencies and Integration Points

They depend on `sys/targets` and `testify/require`. The conversion case indirectly exercises syzkaller syscall descriptions, `prog.Deserialize`, and `csource.WriteLLM`.

## Risks and Edge Cases

Architecture skips mean CI coverage can vary by host. The empty test passes only `ReproSyz: ""`, so it validates empty fallback but not non-empty `ReproC` passthrough. The truncation expectations are exact and therefore guard accidental placeholder or regex changes.

## Test Signals

These tests are strong signals for parser/converter regressions and prompt-size protection. They do not exercise all target OSes or all C repro forms.
