# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crtend.S

AArch64 section terminator object. It defines hidden/global `__EH_FRAME_END__` and `__JCR_END__` symbols in `.eh_frame` and `.jcr`, each aligned to 8 bytes and padded with one pointer-sized slot.

It does not define legacy constructor/destructor list sentinels because this target uses init/fini arrays.
