# File Research: sources/os/plan9/9front/sys/src/9/pc/devvmx.c

## Purpose
Plan 9 `#X` Intel VMX virtualization device. It creates and controls VMX guests through file operations, with guest registers, memory map/EPT configuration, run control, exceptions, interrupts, waits, and floating-point state exposed through a Plan 9 namespace.

## Exposed Interface
- Device table: `vmxdevtab`, device character `X`, name `vmx`.
- Root namespace:
  - `clone`: open by `eve` to create a VM.
  - per-VM directories named by numeric slot.
- Per-VM files:
  - `ctl`: read VM index; write control commands.
  - `regs`: read/write guest registers and VM-exit fields.
  - `status`: read VM state (`init`, `ready`, `running`, `dead`, `ending`).
  - `map`: read/write guest physical memory map backed by global segments and EPT.
  - `wait`: wait for VM exits or IRQ acknowledgements.
  - `fpregs`: read/write saved guest FP state.
- `ctl` commands:
  - `quit`
  - `go [reg=value;...]`
  - `step [reg=value;...]`
  - `stop`
  - `exc <event>`
  - `irq [event]`
  - `extrap <bitmap>`

## Implementation Notes
- Low-level VMX assembly hooks are external: `vmxon`, `vmxoff`, `vmclear`, `vmptrld`, `vmlaunch`, `vmread`, `vmwrite`, `invept`, and `invvpid`.
- `vmxreset()` detects VMX support, verifies BIOS enablement, requires EPT and VPID, and allocates per-CPU `VmxMach` state.
- `vmxstart()` enables VMXE, validates CR0/CR4 fixed bits, performs `VMXON`, creates a VMCS, binds it to the process, and calls `vmcsinit()`.
- `vmcsinit()` initializes VMCS control fields, host state, guest segment/control defaults, EPT pointer, VPID, MSR bitmap/load areas, PAT/EFER handling, FP state, TSC offset, and 64-bit syscall MSR handling.
- `guestregs[]` maps readable/writable textual register names to VMCS fields or `Vmx` struct fields. Special writers enforce kernel-reserved CR0/CR4 bits and update IA32_EFER long-mode-active state.
- EPT mapping:
  - `eptwalk()` lazily allocates EPT page-table pages.
  - `epttranslate()` maps guest physical pages to Plan 9 segment pages or clears mappings.
  - `cmdsetmeminfo()` parses map lines of access flags, memory type, guest range, segment name, and offset.
  - `cmdgetmeminfo()` formats current memory mappings.
  - `cmdclearmeminfo()` frees EPT tables and mapping metadata.
- VM command execution is serialized through `VmCmd` queues. `vmxcmd()` sends commands to the VM kproc and sleeps for completion.
- `vmxproc()` is the per-VM kernel process. It wires itself to a CPU, initializes VMX, processes commands, injects pending exceptions/IRQs, flushes VPID/EPT when needed, restores guest FP/debug/control state, launches/resumes the guest, saves state on VM exit, and records exit status.
- `cmdwait()` formats VM exits using `exitreasons[]` and `except[]`, including qualification, PC/SP, instruction length/info, exception code, guest virtual/physical addresses, and AX for I/O exits.
- `cmdquit()` tears down mappings, clears VMCS, performs `VMXOFF` when the CPU has no remaining VMs, removes the VM table entry, frees the `Vmx`, and exits the kproc.
- `vmxshutdown()` iterates all VMs and issues `quit`.
- Namespace functions (`vmxgen`, `vmxwalk`, `vmxstat`, `vmxopen`, `vmxread`, `vmxwrite`, `vmxremove`, `vmxclose`) implement Plan 9 file semantics and privilege checks.

## Filesystem Relevance
This is highly relevant to virtualization/block-device integration in subset A even though it is not a filesystem. It presents a VM control API as a filesystem-like namespace, and its `map` file binds guest physical memory to Plan 9 segments through EPT mappings.

## Risks / Quirks
- Access is restricted to `eve` for non-directory VM files and clone creation.
- The `cmdsetfpregs()` bounds adjustment appears suspicious: `n = sizeof(FPsave) - n` when `off + n` exceeds the buffer likely should account for `off`.
- VMX correctness depends on CPU-specific MSR control bits and external assembly routines.
- EPT mappings assume fixed/sticky segments and directly index segment maps/pages.
- `go`/`step` use textual inline register assignments, so malformed control input is rejected at command execution time.
