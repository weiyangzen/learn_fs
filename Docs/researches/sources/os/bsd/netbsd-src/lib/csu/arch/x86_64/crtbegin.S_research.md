# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/x86_64/crtbegin.S

x86_64 hand-written `crtbegin` implementation. It defines `.ctors`, `.dtors`, `.eh_frame`, `.jcr`, `__dso_handle`, EH state, and weak helper references.

It implements RIP-relative constructor/destructor helpers: constructors register EH frames and Java classes then walk `.ctors` backward; destructors run `__cxa_finalize`, walk `.dtors`, and deregister EH frames.
