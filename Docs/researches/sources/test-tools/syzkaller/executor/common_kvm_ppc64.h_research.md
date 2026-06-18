# sources/test-tools/syzkaller/executor/common_kvm_ppc64.h

## Purpose

`common_kvm_ppc64.h` implements the PowerPC64 KVM CPU setup pseudo-syscall for syzkaller. It maps the guest memory pages, configures Book3S exception vectors, optionally builds radix MMU page tables, sets CPU register state and endian/user-mode flags, enables hypercall and RTAS coverage, and installs the fuzzer-provided guest instruction blob.

## Important APIs, Types, and Functions

The file defines Book3S interrupt offsets, PPC bit and mask helpers, radix table sizing constants, endian conversion helpers, LPCR/PATB/PRTB constants, fallback KVM capability/ioctl definitions, and setup flags `KVM_SETUP_PPC64_LE`, `KVM_SETUP_PPC64_IR`, `KVM_SETUP_PPC64_DR`, `KVM_SETUP_PPC64_PR`, and `KVM_SETUP_PPC64_PID1`. Helper APIs are `kvmppc_define_rtas_kernel_token`, `kvmppc_get_one_reg`, `kvmppc_set_one_reg`, `kvm_vcpu_enable_cap`, `kvm_vm_enable_cap`, and debug-only `dump_text`. The public entry point is `syz_kvm_setup_cpu()`.

## Control Flow

`syz_kvm_setup_cpu()` reads one `kvm_text`, enables PAPR on the vCPU and nested HV on the VM, maps 24 64K pages with `KVM_SET_USER_MEMORY_REGION`, fetches sregs/regs, and initializes MSR bits for 64-bit mode, optional little endian, problem state, instruction/data relocation, and PID. It fetches KVM's debug instruction opcode and writes it into nearly all exception vectors so unexpected guest exceptions exit reliably; the decrementer vector gets a small recharge sequence from `kvm_ppc64le.S.h` followed by the debug instruction.

If instruction or data relocation is requested, the function builds a radix process table plus PGD/PUD/PMD/PTE pages in guest memory, maps all 24 pages read/write/execute, configures `KVM_PPC_CONFIGURE_V3_MMU`, and sets LPCR radix/process-table bits. It then copies the fuzzer text at the next free guest physical offset, appends a debug instruction sentinel, optionally byte-swaps code and decrementer handler for big-endian execution, writes sregs/regs/LPCR/PID, enables broad hypercall ranges and four KVM-handled RTAS tokens, sets the decrementer expiry, and returns.

## State and Persistence Behavior

All guest-visible state is written into the caller-provided `host_mem`: memory slots, exception vectors, optional radix tables, process table, payload text, and debug sentinel. CPU state persists in KVM vCPU registers, special registers, LPCR, PID, guest debug configuration, enabled capabilities, hypercall bits, RTAS token definitions, and decrementer expiry. The function has no heap allocation and no state outside KVM and the supplied memory.

## Dependencies and Integration Points

The header includes `kvm_ppc64le.S.h` for the decrementer recharge code and relies on Linux KVM PPC structs/constants from the broader executor include environment. It is shared between executor and csource generation and is coupled to the `syz_kvm_setup_cpu` signature in syzkaller's PowerPC KVM descriptions. The guest memory size and page count match `vma[24]` from `dev_kvm.txt`.

## Risks and Edge Cases

The code assumes 64K guest pages and only maps 24 pages. Text size is not clamped before `memcpy`, so syscall descriptions must bound the provided text to available guest memory. Many capability and ioctl calls fail on unsupported hosts, especially nested HV and radix MMU configuration. Big-endian conversion only covers the loaded payload words and decrementer blob. PR mode forcibly enables IR/DR and PID1 because hardware requires translations. Exception-vector debug exits are a mitigation for KVM HV loops but can hide which exact exception happened unless debug output is enabled.

## Test Signals

Signals include successful compilation on ppc64le, `syz_kvm_setup_cpu` returning 0 on hosts with PAPR/nested HV support, expected failure on missing capabilities, execution with LE and BE flags, IR/DR radix page-table boot, PR-mode setup, debug breakpoint exits from unexpected vectors, decrementer recharge behavior, enabled hypercall coverage, RTAS token definitions, and byte-swapped payload inspection under `DEBUG`.
