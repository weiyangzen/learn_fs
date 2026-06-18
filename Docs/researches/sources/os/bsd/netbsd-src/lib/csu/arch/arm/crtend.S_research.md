# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtend.S

ARM section terminator object. It defines hidden `__CTOR_LIST_END__` and `__DTOR_LIST_END__` and emits pointer-sized zero padding for `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

This supports legacy constructor/destructor lists on non-EABI ARM variants.
