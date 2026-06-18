<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/119 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/119

Purpose: This fixture drives `TestParse` for a lockdep key report and locks in the normalized title `INFO: trying to register non-static key in tun_flow_cleanup` plus type `<default>`. It is a parser-regression input, not executable kernel code. The source is `818` bytes across `17` lines, with content hash prefix `6e7e7da57f2c` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `dump_stack`, `register_lock_class`, `__lock_acquire`, `lock_acquire`, `_raw_spin_lock_bh`, `tun_flow_cleanup`; source-path cues include no kernel source paths were intentionally exposed in the body.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `==================================================================`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: INFO: trying to register non-static key in tun_flow_cleanup`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are no special flags, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/119 -->
