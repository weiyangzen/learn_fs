# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtend.S

x86_64 section terminator object. It defines hidden `__CTOR_LIST_END__` and emits 8-byte zero sentinels for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

This terminates the lists used by `crtbegin.S`.
