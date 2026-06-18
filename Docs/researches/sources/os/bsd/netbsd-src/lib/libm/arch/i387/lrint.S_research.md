# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/lrint.S

x86 `lrint` implementation. On i386 it uses x87 `fistpl` through a stack slot; on x86-64 it converts the SSE double argument with `cvtsd2siq`.
