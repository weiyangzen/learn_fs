# sources/test-tools/syzkaller/pkg/mgrconfig/load_test.go

Purpose: Tests syscall selection behavior under different description modes and snapshot handling.

Important test: `TestParseEnabledSyscalls` uses the synthetic test target and table-driven cases for wildcard enablement, exact snapshot-only enablement, manual/automatic modes, and expected enabled/disabled syscall names.

Control flow and state: Each subtest calls `ParseEnabledSyscalls(target, enable, nil, mode)` and asserts target syscall ids are present or absent in the returned slice.

Dependencies and integration: Uses `prog.GetTarget` for `targets.TestOS`/`TestArch64`, plus testify assertions. It protects manager config parsing from accidentally fuzzing automatic-only, manual-only, or snapshot-only descriptions under the wrong mode.

Risks: Disable-list behavior is noted as TODO and not covered. Ordering of returned syscall ids is intentionally map-derived and not asserted.

Test signals: Strong targeted coverage for mode filtering, including the special exact-match behavior that bypasses snapshot checks for exact names.
