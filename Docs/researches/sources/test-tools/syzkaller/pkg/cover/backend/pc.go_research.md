# sources/test-tools/syzkaller/pkg/cover/backend/pc.go

Purpose: normalizes coverage PCs between return-address style values and instruction addresses for different architectures.

Important APIs/types/functions: `PreviousInstructionPC`, `NextInstructionPC`, and `instructionLen`.

Control flow: gVisor PCs bypass adjustment. Other VMs subtract or add an architecture-specific instruction length. ARM clears the low bit after adjustment to normalize THUMB/ARM mode markers. Unknown architectures panic.

State and persistence: pure stateless helpers.

Dependencies and integration: depends on `sys/targets` constants. `report_test.go` uses `PreviousInstructionPC` when converting sanitizer callback return addresses into callback PCs; coverage report endpoints may use these helpers through backend consumers.

Risks: architecture offsets are approximations; amd64/i386 use call length 5, ARM returns 3 then clears the low bit, and MIPS64LE uses 8. Incorrect offsets cause callback mismatch or missed symbols. Panic on new target architectures requires updating this table.

Test signals: no direct test file in this subset; indirect report tests exercise several targets when cross-compilers are available.
