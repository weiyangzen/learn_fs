# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crtend.S

SPARC64 section terminator object. It emits 8-byte-aligned `.quad 0` sentinels for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

Hidden constructor/destructor endpoint symbols are exported.
