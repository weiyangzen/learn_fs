# sources/test-tools/syzkaller/executor/common_kvm_riscv64_syzos.h

## Purpose

`common_kvm_riscv64_syzos.h` implements the RISC-V 64-bit SYZOS guest runtime. It decodes command streams, executes raw instruction blobs, dynamically emits CSR read/write instructions, performs guest memory reads/writes with fences, reports host-observable uexits through MMIO, and provides an unexpected-trap SBI call target for the host-side setup.

## Important APIs, Types, and Functions

The command ABI is `syzos_api_id` with `SYZOS_API_UEXIT`, `SYZOS_API_CODE`, `SYZOS_API_CSRR`, `SYZOS_API_CSRW`, and `SYZOS_API_MEMOP`. `api_call_code` carries inline instructions; generic `api_call_1`, `api_call_2`, and `api_call_5` come from `common_kvm_syzos.h`. Main functions are `guest_main`, `guest_uexit`, `guest_execute_code`, `get_cpu_id`, `guest_handle_csrr`, `guest_handle_csrw`, `guest_handle_memop`, `sbi_ecall`, and `guest_unexp_trap`. CSR instruction generation uses `ENCODE_CSR_INSN` with RISC-V SYSTEM opcode fields.

## Control Flow

`guest_main(size, cpu)` walks the per-vCPU command stream at `RISCV64_ADDR_USER_CODE + cpu * 0x1000`, validates command size and stop id, then uses volatile if/else dispatch to avoid jump-table generation. Code commands run `fence.i` and branch to the supplied instruction buffer. CSR read/write commands write a two-instruction sequence into a per-CPU cache-line slot at `RISCV64_ADDR_SCRATCH_CODE`, execute `fence.i`, and call it with `jalr`; CSR reads place the result in A0 and CSR writes pass the requested value in A0.

Memory operations compute `base + offset`, issue `fence rw,rw`, perform volatile 1/2/4/8-byte loads or stores, fence again, and return read results through the `sscratch` CSR. `guest_uexit()` writes the exit code to `RISCV64_ADDR_UEXIT`, causing the host to observe an MMIO exit. `guest_unexp_trap()` is an aligned trap target that invokes a custom KVM SBI extension/function for unexpected traps.

## State and Persistence Behavior

The runtime avoids normal globals. Persistent effects are guest memory writes, scratch-code writes, CSR changes, `sscratch` read results, and MMIO uexit writes. CPU id is read from `tp`, which the host initializes. The unexpected-trap path communicates through an SBI ecall rather than local state.

## Dependencies and Integration Points

The header depends on `common_kvm_syzos.h` for guest-section attributes and shared API structs, and `kvm.h` for RISC-V guest addresses. It integrates with `common_kvm_riscv64.h`, which maps user code, scratch code, exception vectors, and sets PC/SP/TP/SSTATUS/STVEC/GP. API ids must match `sys/linux/dev_kvm_riscv64.txt`.

## Risks and Edge Cases

The no-relocation constraint makes compiler-emitted globals and jump tables hazardous; this file uses if/else chains and generated scratch instructions to reduce that risk. `guest_handle_memop()` treats any op other than 1 as a read and any length other than 1/2/4 as 8 bytes. CSR ids and target addresses are fuzzer-controlled, so illegal instruction and access faults are expected coverage paths. Scratch-code slots assume `MAX_CACHE_LINE_SIZE` separation is enough for all vCPUs. Read results in `sscratch` require host or follow-up guest code to inspect the CSR.

## Test Signals

Signals include build checks for the guest section, command streams ending in `UEXIT_END`, malformed command bounds returning without overrun, raw code execution after `fence.i`, CSR read/write to safe CSRs, illegal CSR fault behavior through `guest_unexp_trap`, memory read/write widths with `sscratch` result verification, per-vCPU scratch separation, and host assertion of uexit MMIO codes.
