# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crtend.S

EABI ARM section terminator object. It emits EABI attributes for `wchar_t`, floating-point use, stack alignment, and enum size.

It defines hidden `__EH_FRAME_END__` and `__JCR_END__` sentinels; legacy `.ctors/.dtors` sentinels are not used in this array-based path.
