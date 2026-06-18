# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crtend.S

m68k section terminator object. It defines hidden `__CTOR_LIST_END__` and `__DTOR_LIST_END__`, then emits zero sentinels for constructor, destructor, EH frame, and JCR sections.

This supports legacy constructor/destructor traversal.
