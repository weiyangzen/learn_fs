# sources/test-tools/syzkaller/pkg/manager/seeds_test.go

Purpose: Tests seed `# requires:` architecture matching.

Important test: `TestRequires` parses positive and negative architecture requirements and checks `checkArch` behavior for `amd64` and `riscv64`.

Control flow and state: The test calls `parseRequires` on synthetic comment lines and then evaluates the resulting map. It validates that `arch=amd64` admits only amd64, and that negative architecture requirements can exclude riscv64 while allowing amd64.

Dependencies and integration: Directly covers helpers used by `parseProg` before seed deserialization. This is important because requirements are checked early to avoid deserializing unsupported programs on the wrong architecture.

Risks: It does not cover `MatchRequirements` combinations, manual constraints, strict vs non-strict deserialization, long program rejection, `fail_nth`, corpus DB cleanup, or candidate flag migration.

Test signals: Narrow but useful coverage for architecture gating in seed files.
