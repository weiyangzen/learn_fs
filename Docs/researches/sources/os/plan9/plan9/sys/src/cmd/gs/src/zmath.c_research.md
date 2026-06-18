# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmath.c

PostScript math and random-number operators. It registers trigonometric/logarithmic functions, square root, exponentiation, and `rand`/`srand`/`rrand`.

Each numeric operator validates real/integer operands through `real_param` or `num_params`, calls the C math library or Ghostscript fixed helpers as appropriate, and writes back integer or real results. Trigonometric functions use PostScript degrees rather than C radians. `atan` handles the two-argument PostScript form and normalizes results.

The random operators expose Ghostscript’s internal random state: `rand` pushes the next pseudo-random integer, `srand` seeds from an integer operand, and `rrand` returns the current seed/state. The file is straightforward operand conversion and range/error mapping around math helpers.
