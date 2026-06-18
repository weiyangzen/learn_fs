# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtend.S

MIPS section terminator object. It emits constructor/destructor list endpoints and pointer-sized padding for `.eh_frame` and `.jcr`.

Alignment and sizes are derived from `PTR_SCALESHIFT` and `_MIPS_SZPTR`.
