# File Research: sources/os/plan9/9front/sys/src/cmd/gs/arch.h

Architecture selection header for Ghostscript build integration. It includes the per-architecture header based on compiler target macros such as `T386`, `Tmips`, `Tarm`, `Tamd64`, etc. Unknown architectures intentionally trigger invalid source text telling the maintainer to update the switch.
