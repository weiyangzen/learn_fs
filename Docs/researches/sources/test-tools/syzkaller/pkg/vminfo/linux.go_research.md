# sources/test-tools/syzkaller/pkg/vminfo/linux.go

## Purpose

`linux.go` extracts Linux-specific VM machine information: required/check files, kernel modules, core kernel text range, CPU info, and KVM module parameters.

## Important APIs, Types, And Functions

`linux.RequiredFiles` and `CheckFiles` list VM files/globs. `machineInfos` returns `linuxReadCPUInfo` and `linuxReadKVMInfo`. `parseModules` parses `/proc/modules`, reads per-module `.text` addresses, adds the core kernel from `_stext`/`_etext`, and sorts modules. `linuxModuleTextAddr`, `linuxParseCoreKernel`, `linuxReadCPUInfo`, `allEqual`, and `linuxReadKVMInfo` implement parsing/formatting.

## Control Flow, State, Dependencies, And Integration

The code operates on the virtual `filesystem` built from `flatrpc.FileInfo`, not live host paths. gVisor and Starnix skip module parsing. CPU info groups repeated keys and prints either a single value or comma-joined differing values. KVM info walks virtual `/sys/module/kvm*/parameters`.

## Risks And Test Signals

Regexes assume Linux `/proc/modules` and kallsyms formats. Module size correction can underflow if addresses are inconsistent. CPU parsing ignores lines without exactly one colon. Tests in `linux_test.go` cover Linux syscall checks, host KVM output formatting, and canned CPU info across architectures.
