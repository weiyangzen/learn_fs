# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdt_impl.h

## Role

Defines private SDT provider/probe implementation structures used by the DTrace SDT module and kernel runtime linker patching.

## Key Interfaces

- x86 instruction constants: `SDT_CALL`, `SDT_NOP`, `SDT_RET`, and `SDT_OFF_RET_IDX`.
- `sdt_instr_t` is `uint8_t` on x86 and `uint32_t` elsewhere.
- `sdt_provider_t` describes a provider name, probe-name prefix, stability attributes, privilege, and provider ID.
- `sdt_probe_t` tracks provider, name allocation, DTrace ID, owning module, load count, primary-module status, patch point, saved/patch instruction values, tail-call status, and list/hash links.
- `sdt_argdesc_t` maps provider/probe/argument index to native and translated DTrace argument types.
- Exports `sdt_providers[]`, `sdt_getargdesc()`, and `sdt_mode()`.

## Risk Notes

This header is coupled to instruction patching and module load accounting. Architecture-specific instruction sizes and tail-call handling must match krtld and SDT activation logic exactly.
