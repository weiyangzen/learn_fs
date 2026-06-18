# sources/test-tools/syzkaller/dashboard/config/linux/bits/comedi.yml

Purpose: enables COMEDI subsystem coverage, including legacy manual device configuration and selected USB, misc, PCI, PCMCIA, and x86 ISA drivers.

Important keys: appends `comedi.comedi_num_legacy_minors=4` to the command line, enables `COMEDI`, USB drivers (`COMEDI_DT9812`, `NI_USB6501`, `USBDUX*`, `VMK80XX`), misc drivers, selected PCI/PCMCIA drivers, and many ISA drivers gated to `x86_64` with `ISA_BUS`.

Control flow: declarative Kconfig fragment.

State and persistence: affects generated `.config` and boot command line.

Dependencies and integration points: Linux COMEDI Kconfig, syzkaller COMEDI descriptions/ioctls, USB/PCI/ISA bus support, and x86_64 manager profiles.

Risks: broad legacy driver enablement can expose old code with unusual dependencies and boot/build issues. ISA gating avoids non-x86 architectures but still relies on x86_64 Kconfig availability. The legacy minors command-line setting changes device namespace and must match fuzzing expectations.

Test signals: generated kernels should build with COMEDI drivers and expose configurable COMEDI devices/ioctls for fuzzing.
