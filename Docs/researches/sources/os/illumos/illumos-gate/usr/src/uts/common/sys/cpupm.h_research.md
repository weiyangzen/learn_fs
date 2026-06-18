# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpupm.h

## Role

Small CPU power-management public header that bridges common CPU state and machine-specific CPU PM support.

## Interface

- Includes:
  - `sys/types.h`
  - `sys/cpuvar.h`
  - `sys/cpupm_mach.h`
- Declares:
  - `cpupm_set_supp_freqs(cpu_t *, int *, uint_t)`

## Research Relevance

A narrow helper interface for recording supported CPU frequencies. It connects platform-specific PM code to common CPU structures.
