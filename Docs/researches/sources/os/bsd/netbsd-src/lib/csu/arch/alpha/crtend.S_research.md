# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crtend.S

Alpha section terminator object. It places zero sentinels at the end of `.ctors`, `.dtors`, `.eh_frame`, and `.jcr`.

The constructor/destructor list endpoints are exported as hidden `__CTOR_LIST_END__` and `__DTOR_LIST_END__`.
