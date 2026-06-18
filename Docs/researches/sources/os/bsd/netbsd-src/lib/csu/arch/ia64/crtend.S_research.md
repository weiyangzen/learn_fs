# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtend.S

IA-64 section terminator object. It places 8-byte-aligned `.quad 0` sentinels in `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

Hidden constructor/destructor endpoint symbols are exported for the common list walkers.
