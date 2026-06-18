# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/5

Purpose: Negative OpenBSD fixture for kernel relinking failure text. It has no expected title and should not parse as a crash.

Important parser APIs and patterns: `openbsdOopses` has a `kernel:` oops group with suppressing regex `reorder_kernel`, but this fixture contains only `reorder_kernel: kernel relinking failed; see ...`. It lacks `panic:`, `uvm_fault(`, `kernel: page fault trap`, `kernel: protection fault trap`, or witness signatures.

Control flow: single diagnostic line from OpenBSD kernel relinking infrastructure. No DDB prompt, stack, or stopped frame exists.

State and persistence: static no-crash fixture preserving a path to the relink log. It represents VM setup/boot noise.

Dependencies and integration: protects `ContainsCrash` from treating relinking failure as a kernel crash, while still allowing the `reorder_kernel` suppressor to filter real `kernel:` fault lines if needed.

Risks: overbroad matching on the word `kernel` could create false positives during OpenBSD boot or relink failures.

Test signals: expected behavior is no report.
