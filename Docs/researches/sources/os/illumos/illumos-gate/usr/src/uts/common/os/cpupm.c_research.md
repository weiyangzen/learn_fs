# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpupm.c

## Role

`cpupm.c` contains a compatibility/helper routine for formatting supported CPU frequencies for the `cpu_info` kstat field `supported_frequencies_Hz`.

It is distinct from `cpu_pm.c`: this file only prepares a colon-separated frequency string and passes it to `cpu_set_supp_freqs()`.

## Function

`cpupm_set_supp_freqs()` accepts a CPU, an array of speed percentages or platform speed values, and a count.

If `speeds` is `NULL`, it calls `cpu_set_supp_freqs(cp, NULL)`, causing the CPU layer to report only the current clock.

If speeds are provided, it:

- Allocates a `uint64_t` array of frequencies.
- Converts input speeds to Hz with `CPUPM_SPEED_HZ(cp->cpu_type_info.pi_clock, speeds[j])`.
- Reverses the input order into the Hz array.
- Builds a colon-separated string of unsigned 64-bit frequency values.
- Calls `cpu_set_supp_freqs()` to update the CPU kstat backing string.
- Frees temporary arrays.

## Research Notes

This file is a narrow bridge between CPU power-management speed data and the generic CPU kstat export path in `cpu.c`. The fixed maximum decimal width is based on the maximum `uint64_t` string length.
