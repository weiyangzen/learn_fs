# sources/test-tools/syzkaller/executor/common_kvm_syzos.h

## Purpose

`common_kvm_syzos.h` provides shared definitions for SYZOS guest runtimes across architectures. It centralizes compiler attributes for copied guest code and defines common command payload headers used by architecture-specific KVM command decoders.

## Important APIs, Types, and Functions

The file defines `noinline`, `always_inline`, `__no_stack_protector`, `__addrspace_guest`, `__optnone`, and `GUEST_CODE`. `GUEST_CODE` places functions in the `guest` section and disables stack protector behavior so the host can copy a contiguous guest-code section into guest memory. It declares `__start_guest` and `__stop_guest` section boundaries. Shared command structs are `api_call_header`, `api_call_1`, `api_call_2`, `api_call_3`, and `api_call_5`.

## Control Flow

There is no runtime control flow in this header. Its macros influence how functions in `common_kvm_*_syzos.h` compile, where they are linked, and whether they are safe to copy into the guest. Architecture-specific `guest_main()` implementations consume the shared `api_call_header` and fixed-width argument structs while walking command streams.

## State and Persistence Behavior

No mutable state is defined here. The only declared state is linker-provided guest-section start/end symbols. The struct layouts are part of the persistent ABI between syzkaller-generated command streams, host pseudo-syscalls, and in-guest decoders.

## Dependencies and Integration Points

This header assumes syzkaller executor typedefs such as `uint64` are available from the including environment. It is included by the AMD64, ARM64, and RISC-V SYZOS headers and indirectly by host-side KVM setup files that need guest section symbols. Compiler-specific branches support Clang address-space annotations and GCC fallback stack-protector disabling.

## Risks and Edge Cases

If `GUEST_CODE` does not place all required functions into one copyable section, host setup will omit code. If stack protector instrumentation is emitted, guest code may reference unavailable globals. GCC versions before 11 use an optimize-attribute fallback for stack-protector disabling. Struct layout changes or argument-count mismatches break all architecture command ABIs. `__addrspace_guest` is active only under Clang, so compiler differences must be covered by builds.

## Test Signals

Primary signals are successful guest-section link symbols, no stack-protector references in generated guest code, architecture guest headers compiling under supported GCC and Clang versions, stable `api_call_*` struct sizes, and host-side copy/install code seeing a nonzero `__stop_guest - __start_guest` range.
