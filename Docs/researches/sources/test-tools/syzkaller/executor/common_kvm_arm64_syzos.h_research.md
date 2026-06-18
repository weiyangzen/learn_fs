# sources/test-tools/syzkaller/executor/common_kvm_arm64_syzos.h

## Purpose

`common_kvm_arm64_syzos.h` implements the ARM64 SYZOS guest runtime. It decodes guest command streams, executes raw AArch64 instruction blobs, dynamically emits MRS/MSR instructions, invokes SMC/HVC/SVC calls, writes guest memory, configures GICv3 interrupts and vector handling, and programs a virtual ITS/LPI setup for interrupt fuzzing from inside the guest.

## Important APIs, Types, and Functions

The command ABI is `syzos_api_id`, with payload structs `api_call_uexit`, `api_call_code`, `api_call_smccc`, `api_call_irq_setup`, `api_call_memwrite`, and `api_call_its_send_cmd`. `guest_main(size, cpu)` dispatches to `guest_uexit`, `guest_execute_code`, `guest_handle_mrs`, `guest_handle_msr`, `guest_handle_smc`, `guest_handle_hvc`, `guest_handle_svc`, `guest_handle_eret`, `guest_handle_irq_setup`, `guest_handle_memwrite`, `guest_handle_its_setup`, and `guest_handle_its_send_cmd`.

Low-level helpers include `flush_cache_range`, `reg_to_msr`, `reg_to_mrs`, `get_cpu_id`, raw MMIO `readl`/`writel`/`readq`/`writeq`, `guest_udelay`, and RWP polling helpers. Interrupt setup uses `gicv3_dist_init`, `gicv3_enable_redist`, `gicv3_cpu_init`, `gicv3_irq_enable`, `one_irq_handler`, `guest_irq_handler`, and `guest_vector_table`. ITS support is built around `its_cmd_block`, `its_send_cmd`, table installers, command encoders, `guest_setup_its_mappings`, `gic_rdist_enable_lpis`, `configure_lpis`, and `guest_prepare_its`.

## Control Flow

`guest_main(size, cpu)` starts at `ARM64_ADDR_USER_CODE + cpu * 0x1000`, validates command bounds, dispatches by API id, advances by `cmd->size`, and emits `UEXIT_END` when the stream is exhausted. `guest_execute_code()` flushes D-cache and I-cache over the supplied instruction range before branching to it. MRS/MSR handlers synthesize one privileged instruction plus `RET` into per-CPU scratch cache lines at `ARM64_ADDR_SCRATCH_CODE`, flush that scratch code, and branch through it with x0 used for the operand/result convention.

SMC, HVC, and SVC handlers load x0-x5 from the command and execute immediate `#0`, clobbering the normal SMCCC scratch registers. IRQ setup initializes distributor and redistributors, enables SPI lines, installs `guest_vector_table` into `VBAR_EL1`, and clears interrupt masks. The assembly IRQ entry saves general registers plus ELR/SPSR into `ex_regs`, calls `guest_irq_handler`, restores state, and returns with `eret`; the C handler acknowledges IAR0/IAR1, emits `UEXIT_IRQ`, writes EOIR, and deactivates via DIR.

ITS setup configures GITS_BASER tables, command queue, redistributor LPI property/pending tables, and initial MAPC/MAPD/MAPTI mappings. Later `guest_handle_its_send_cmd()` deliberately uses volatile if-chains instead of a switch, encodes the requested ITS command, and writes it to the command queue by advancing GITS_CWRITER.

## State and Persistence Behavior

The runtime stores no normal C globals because the guest section is copied without relocation handling. Persistent state lives in guest physical memory: user code pages, per-CPU scratch code, GIC/ITS MMIO registers, ITS command/table memory, LPI property and pending tables, and host-observed uexit MMIO. Per-CPU identity comes from `TPIDR_EL1`, set by host setup. Interrupt vector code and handlers are compiled into the guest section and installed by address at runtime.

## Dependencies and Integration Points

The header depends on `common_kvm_syzos.h` and `kvm.h` for guest-section attributes, shared command structs, `executor_fn_guest_addr`, address layout, GIC/ITS constants, and bit macros. It integrates with `common_kvm_arm64.h`, which maps the GIC, redistributor, user-code, scratch, stack, dirty-page, executor-code, and ITS-table regions. API ids must stay synchronized with `sys/linux/dev_kvm_arm64.txt`.

## Risks and Edge Cases

The code carefully avoids jump tables, global constants, and relocations; compiler changes that emit ADRP, literal pools, vectorized stores, or helper calls can break copied SYZOS code. Cache maintenance is mandatory for generated code. MMIO polling uses assertion uexits to avoid infinite hangs, but many setup writes assume the host mapped matching devices. `guest_handle_irq_setup()` bounds SPI count but trusts CPU count. ITS command encoders depend on precise bit positions and table sizing, and `SYZOS_NUM_IDBITS` fixes the property table to 64K. Memory write commands can target arbitrary guest physical addresses by design.

## Test Signals

Good coverage includes building the guest section with ADRP validation, executing raw code blobs after cache flush, generated MRS/MSR access to safe registers, SMC/HVC/SVC exits, `ERET` behavior, bounded malformed command streams, VGICv3 setup followed by injected IRQ and `UEXIT_IRQ`, MMIO writes of 1/2/4/8 bytes, ITS setup with MAPD/MAPC/MAPTI mappings, each supported ITS command path, and assertion behavior when RWP polling never clears.
