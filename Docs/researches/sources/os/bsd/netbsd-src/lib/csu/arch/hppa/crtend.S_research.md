# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crtend.S

HPPA section terminator object. It places `.long 0` sentinels in `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

The constructor and destructor list endpoints are exported and hidden.
