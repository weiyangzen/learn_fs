<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/122 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/122

Purpose: This fixture drives `TestParse` for a usercopy hardening report and locks in the normalized title `BUG: bad usercopy in kvm_vcpu_ioctl_set_cpuid2` plus type `BUG`. It is a parser-regression input, not executable kernel code. The source is `3354` bytes across `56` lines, with content hash prefix `f46914a7c7f6` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `__check_object_size`, `lock_release`, `check_stack_object`, `check_noncircular`, `__might_sleep`, `kvm_vcpu_ioctl_set_cpuid2`; source-path cues include `mm/usercopy.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `parse fixture`, the key body signal begins with: `usercopy: kernel memory overwrite attempt detected to ffff8801d21c9bd4 (kvm_vcpu) (1320 bytes)`. The expected parsed crash metadata is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists expected parser state as headers: `TITLE: BUG: bad usercopy in kvm_vcpu_ioctl_set_cpuid2; TYPE: BUG; PANICKED: Y`. If a `REPORT:` block is present, `ParseTest.Report` must match the extracted report bytes; otherwise the log body itself is the regression oracle. Flags are `PANICKED=Y`, and these control whether the result is considered corrupted, panicked, suppressed, or tied to an executor.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: an intentionally empty guilty file must remain empty rather than falling back to a misleading helper path, panic detection is part of the expected result. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/122 -->
