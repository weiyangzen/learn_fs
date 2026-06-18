# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtend.S

VAX section terminator object. It defines hidden constructor/destructor list endpoints and zero padding for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

This terminates the legacy lists used by VAX startup assembly.
