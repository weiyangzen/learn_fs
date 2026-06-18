# File Research: sources/os/bsd/netbsd-src/lib/libnvmm/nvmm.h

Public libnvmm API header. It wraps kernel NVMM ioctl/state headers and defines `NVMM_USER_VERSION` 2, noting version 2 added `nvmm_vcpu::stop`.

It defines userland handles for machines, VCPUs, assist callbacks, I/O exits, memory exits, and protection bits. Public functions cover initialization, capabilities, machine/VCPU lifecycle and configuration, state get/set, event injection, running, GPA/HVA mapping, GVA-to-GPA and GPA-to-HVA lookup, I/O/memory assistance, raw control ioctl, debug dump, and VCPU stop.
