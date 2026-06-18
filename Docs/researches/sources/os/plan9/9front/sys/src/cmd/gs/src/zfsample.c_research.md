# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfsample.c

## Purpose
Samples an arbitrary PostScript procedure over a hypercube and converts it into a FunctionType 0 sampled function.

## Key Functions
- `zbuildsampledfunction()` reads the source procedure and sampled-function dictionary, allocates a temporary FunctionType 0 structure, and starts sampling.
- `valid_cube_size()` ensures requested sample data fits within the 64 KiB string limit.
- `determine_sampled_data_size()` chooses default per-input sample counts when `Size` is absent.
- `cube_build_func0()` validates `Domain`, `Range`, `BitsPerSample`, `Order`, and `Size`, and allocates sample storage.
- `sampled_data_setup()` allocates the sampling enumerator and pushes protected e-stack state.
- `sampled_data_sample()` pushes input coordinates and executes the procedure.
- `sampled_data_continue()` validates stack balance, clamps/scales output values, stores samples MSB-first, and advances indexes.
- `sampled_data_finish()` rebuilds the final sampled function and returns an executable function closure.

## Important Behavior
- Sample data is capped at `MAX_DATA_SIZE` (`0x10000`), with up to 16 inputs and 128 outputs.
- Default cube side lengths shrink as dimensionality increases to keep data bounded.
- Three padding operands are intentionally placed below procedure inputs to tolerate malformed tint transforms that pop too much.
- Outputs are clamped to `Range` before quantization.
- Estack storage protects the procedure, finish callback, and enumerator from the sampled procedure.

## Research Notes
This file is a continuation-heavy bridge from executable PostScript procedures to static sampled function data.
