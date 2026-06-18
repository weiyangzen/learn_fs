# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/lrint.S

Alpha `lrint` implementation. It converts `fa0` to integer with `cvttq`, stores/loads through the stack to move the FP result into `v0`, and returns.
