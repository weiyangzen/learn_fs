# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/37

Purpose: OpenBSD panic fixture for a corrupted-looking `vop_generic_badop` message. Expected title is `panic: vop_generic_badop`; expected type is `DoS`.

Important parser APIs and patterns: `ctorOpenbsd` suppresses exact `panic: vop_generic_badop`, but this fixture’s expected metadata does not mark it suppressed. The title is extracted through the DDB `show panic` rule: `ddb{...}> show panic ... *cpu0: vop_generic_badop ... ddb{...}> trace`, which normalizes the garbled initial panic text.

Control flow: raw panic text appears as `panic: vop_generic_bapdoapn` followed by a malformed `iStopped at`, then a stack through `vop_generic_badop`, `VOP_STRATEGY`, `bwrite`, `VOP_BWRITE`, `ufs_mkdir`, `VOP_MKDIR`, `domkdirat`, and syscall. DDB `show panic` supplies the canonical CPU panic line.

State and persistence: static fixture preserving multi-CPU panic state and a second CPU assertion. It tests recovery from partially corrupted serial output.

Dependencies and integration: exercises OpenBSD DDB panic-title extraction, DoS type metadata, and stack capture despite malformed early lines.

Risks: relying only on the first `panic:` line would produce the wrong title. Suppression matching must remain intentionally tied to full output rules.

Test signals: exact title `panic: vop_generic_badop`; stack frame `vop_generic_badop+0x1b`.
