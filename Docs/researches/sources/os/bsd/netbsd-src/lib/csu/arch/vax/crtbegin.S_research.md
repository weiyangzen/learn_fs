# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/vax/crtbegin.S

VAX hand-written `crtbegin` implementation. It defines legacy constructor/destructor lists, EH/JCR anchors, `__dso_handle`, state flags, and weak helper references.

Constructor logic registers EH frames, optionally registers Java classes, and walks constructors backward from `__CTOR_LIST_END__`. Destructor logic finalizes shared objects, walks `.dtors`, and deregisters frames.
