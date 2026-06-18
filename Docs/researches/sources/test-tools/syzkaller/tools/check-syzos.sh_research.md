<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-syzos.sh -->
# sources/test-tools/syzkaller/tools/check-syzos.sh

## Purpose

SYZOS binary checker that rejects problematic data accesses in the syz-executor `guest` ELF section.

## Important APIs, Types, and Functions

Uses `TARGETOS`, `BUILDOS`, `TARGETARCH`, target-prefixed objdump fallback, `awk`/`gawk`, grep/sed, section headers, disassembly, and arch-specific patterns.

## Control Flow

Skips non-Linux/cross-build/unsupported archs, locates `bin/${TARGETOS}_${TARGETARCH}/syz-executor`, verifies `guest`, disassembles it, then flags amd64 RIP-relative references outside the section and arm64/riscv64 `adrp`/`auipc` accesses.

## State and Persistence Behavior

Reads the executor binary only; all section bounds and matches are process-local.

## Dependencies and Integration Points

Requires a built executor and usable objdump; integrated into SYZOS build validation.

## Risks and Edge Cases

Objdump text parsing is version-sensitive; non-amd64 checks are instruction-pattern heuristics; guest-end boundary handling is approximate.

## Test Signals

Run after linux amd64/arm64/riscv64 executor builds, including negative binaries with synthetic out-of-section references.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-syzos.sh -->
