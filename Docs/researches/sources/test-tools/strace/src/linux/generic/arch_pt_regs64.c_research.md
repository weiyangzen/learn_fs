# sources/test-tools/strace/src/linux/generic/arch_pt_regs64.c

Purpose: declares or decodes `generic` ptrace register structures used by generic Linux support.

Important APIs/types/functions: decode_pt_regs64; notable register references include none in this file.

Control flow: used during ptrace register fetch/dump paths, often as shared fallback code.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on kernel ptrace register layouts and generic register printers.

Risks/test signals: validate register dumps against kernel headers and known ptrace output.

Source-read signal: reviewed complete local file (5 lines).
