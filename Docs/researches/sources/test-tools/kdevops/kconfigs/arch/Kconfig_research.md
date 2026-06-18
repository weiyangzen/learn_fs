# sources/test-tools/kdevops/kconfigs/arch/Kconfig

Purpose: Kconfig fragment that selects the generic target architecture for kdevops workflows and exports architecture capability flags.

Important APIs/types/functions: defines a `choice` named by prompt `Target architecture` with default from `scripts/get_target_arch.sh`. Options are `TARGET_ARCH_X86_64`, `TARGET_ARCH_ARM64`, and `TARGET_ARCH_PPC64LE`, all marked `output yaml`. ARM64 and PPC64LE select the internal `HAVE_ARCH_64K_PAGES` capability.

Control flow: menuconfig selects exactly one target architecture. The selected symbol is emitted to generated YAML and can gate workflow defaults, host setup, and filesystem/block-size options.

State/persistence behavior: state is held in `.config` and generated extra vars. `HAVE_ARCH_64K_PAGES` is a kdevops-only capability, not a Linux kernel Kconfig symbol, and indicates that 64k page-size workflows can be offered.

Dependencies/integration: consumed by workflow Kconfigs, template generation, and architecture-aware roles. The target host ISA itself is described as selected under bring-up methods, so this file is a generic workflow selector rather than all hardware configuration.

Risks/test signals: the default depends on shell execution and can be wrong under cross-target setups. Test signals are valid Kconfig parsing, one selected architecture, expected YAML output, and correct gating of 64k-page options.
