<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xraw.c -->
## sources/test-tools/strace/tests/arch_prctl-success-Xraw.c

Purpose: Raw xlat variant of the injected-success `arch_prctl` test.

Important APIs/types/functions: Defines `XLAT_RAW 1` and includes `arch_prctl-success.c`.

Control flow: Compiles injected return behavior with raw numeric formatting for xlat-controlled fields.

State and persistence: No wrapper-local state.

Dependencies and integration: Completes the raw xlat lane for arch_prctl success handling.

Risks: Same injection argument and macro-coupling risks as `arch_prctl-success.c`.

Test signals: Expected output combines injected result annotations with numeric command/xfeature rendering.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/arch_prctl-success-Xraw.c -->
