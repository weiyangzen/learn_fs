# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc/crtend.S

SPARC section terminator object. It emits 4-byte-aligned zero sentinels for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

Hidden constructor/destructor endpoint symbols are exported.
