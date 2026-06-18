# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crtend.S

i386 section terminator object. It exports hidden `__CTOR_LIST_END__` and appends zero sentinels to `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

This pairs with the i386 assembly `crtbegin.S` legacy list walker.
