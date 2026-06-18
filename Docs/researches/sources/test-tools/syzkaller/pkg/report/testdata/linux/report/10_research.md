<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/10 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/10

Purpose: This fixture drives `TestParse` for a fault report and locks in the normalized title `BUG: unable to handle kernel paging request in __call_rcu` plus type `MEMORY_SAFETY_BUG`. It is a parser-regression input, not executable kernel code. The source is `310` bytes across `8` lines, with content hash prefix `7a0fd3c2ceb9` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__call_rcu`; source-path cues include `kernel/rcu/tree.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `BUG: unable to handle kernel paging request at 00000000ffffff8a`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: unable to handle kernel paging request in __call_rcu; ALT: bad-access in __call_rcu; TYPE: MEMORY_SAFETY_BUG; CORRUPTED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `CORRUPTED=Y`, `ALT=bad-access in __call_rcu`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, corruption detection is part of the expected result, alternate-title generation must remain stable. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/10 -->
