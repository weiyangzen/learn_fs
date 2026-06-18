# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/14

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/14` is a compact NetBSD UBSan report fixture. It contains the expected title `UBSan: Undefined behavior` and a single boot-time diagnostic line reporting a misaligned member access in ACPICA resource parsing: `rsaddr.c:331:22`, involving `union AML_RESOURCE`.

Unlike reports `12` and `13`, this file has no panic prefix, stack trace, DDB stop, process table, locks, or registers. Its purpose is to validate the generic NetBSD `UBSan:` detector for sanitizer output that does not include enough stack context to name a kernel function.

## Important APIs, Types, And Functions

The relevant syzkaller parser entry is the generic `UBSan:` oops in `netbsdOopses`, which has:

- header trigger `[]byte("UBSan:")`;
- title pattern `UBSan:`;
- fixed output format `UBSan: Undefined behavior`.

The runtime type named in the diagnostic is `union AML_RESOURCE`, from NetBSD's imported ACPICA code under `sys/external/bsd/acpica/dist/resources/rsaddr.c`. There are no stack frames for `bsd.symbolizeLine` to rewrite and no function name for the parser to capture.

## Control Flow

The represented control flow is intentionally minimal:

1. NetBSD emits normal boot log lines.
2. UBSan reports undefined behavior in ACPICA code at timestamp `1.000003`.
3. The syzkaller reporter sees the `UBSan:` marker and classifies the log as a crash-like report with the generic UBSan title.

There is no panic path through `vpanic`, no `HandleTypeMismatch` stack frame, and no DDB command output. The parser must therefore avoid requiring a full panic traceback before recognizing UBSan output.

## State And Persistence Behavior

The fixture is static testdata with no mutable state. The only captured runtime state is the source location and misaligned address in the UBSan message. Because no DDB state is present, this file checks the low-context edge case where a report has a sanitizer finding but lacks stack, locks, process, or register diagnostics.

## Dependencies

The file depends on the textual marker `UBSan:` and NetBSD's sanitizer wording for undefined behavior. It also depends on the testdata convention of a `TITLE:` header followed by raw log text. It does not depend on kernel symbols, stack-frame formatting, or DDB output.

The fixture is closely related to `sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/10` and `11`, which are similarly short UBSan fixtures. This file broadens that coverage to an ACPICA `union AML_RESOURCE` misalignment report.

## Integration Points

The integration point is the fallback path in `netbsdOopses`. The report is discovered by the same `forEachFile` test harness as full panic reports, but it exercises a different branch: generic UBSan detection without a crash-site function.

In kernel-domain terms, the diagnostic originates in ACPICA resource parsing rather than syscall-triggered networking or VM code. For syzkaller, that distinction is secondary because the fixture lacks stack context and intentionally buckets to the generic UBSan title.

## Risks

The main risk is false negatives if parser logic becomes too dependent on `panic:` or stack traces for NetBSD sanitizer reports. A secondary risk is false positives: a broad `UBSan:` marker can classify any UBSan boot line as a crash, so ignore rules and higher-level crash triage need to decide whether these short boot diagnostics are actionable.

Another risk is title granularity. Because this fallback title is intentionally generic, multiple distinct UBSan findings can collapse into `UBSan: Undefined behavior` when no richer stack context is available.

## Test Signals

The expected signal is the exact title `UBSan: Undefined behavior`. Passing tests show that `ContainsCrash` and `Parse` recognize a bare UBSan line and do not require stack symbolization or NetBSD DDB output. The absence of stack frames is itself a test signal: `Symbolize` should leave the report effectively unchanged.
