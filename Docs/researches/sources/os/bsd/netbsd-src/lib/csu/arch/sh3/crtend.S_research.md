# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtend.S

SH3 section terminator object. It defines hidden `__CTOR_LIST_END__` and emits zero sentinels for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

This terminates the lists walked by the SH3 assembly `crtbegin.S`.
