# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/34

Purpose: Negative OpenBSD fixture for failed DDB command automation at a login prompt. It has no expected title and should not parse as a crash.

Important parser APIs and patterns: this file is relevant to false-positive prevention in `containsCrash` and `simpleLineParser`/BSD parsing. It contains command words such as `show panic`, `show registers`, `machine ddbcpu`, and `show malloc`, but none of the OpenBSD oops headers (`panic:`, `uvm_fault(`, `kernel: page fault trap`, `witness:`, or `lock order reversal:`).

Control flow: the VM is at `OpenBSD/amd64 ... login:`. Automation sends DDB-like commands to the login prompt, receives password prompts and `Login incorrect`, and never enters DDB or emits a kernel stack.

State and persistence: static no-crash fixture preserving console interaction state only.

Dependencies and integration: protects OpenBSD report extraction from treating scripted crash-collection commands as evidence of a crash when the VM is merely at a login prompt.

Risks: command keywords are tempting anchors for boundary logic. Crash detection must be driven by oops signatures, not by diagnostic command names.

Test signals: expected result is no report. Any title, especially one inferred from `show panic`, is a regression.
