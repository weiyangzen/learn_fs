## sources/test-tools/syzkaller/tools/arm64/registers.go

This generator converts ARM64 system-register tables into syzkaller KVM register ID descriptions for `dev_kvm.txt`. `main` reads an input table file, prints generated header/footer, system register IDs, and extra core register IDs.

`printSysRegIDs` skips comments/blank lines, expands wildcard lines, processes each line, and emits comma-separated hex IDs. `processLine` parses five binary operands, treating `-` as zero, and calls `arm64KVMRegID`. `expandLine` recursively expands `n[...]` bit wildcards into all permutations. `arm64KVMRegID` combines operands with constants from Linux KVM ARM64 UAPI. `printCoreRegs` emits hard-coded extra IDs observed from QEMU/KVM.

State is stdout-only generation. Dependencies include regexp/string parsing and syzkaller `tool.Failf`. Integration is manual code generation for syzkaller descriptions. Risks include parsing assumptions about table format, recursive expansion size, hard-coded Linux v6.10.2 constants/extra registers, and emitting parse errors into stdout alongside generated data. No tests were observed.
