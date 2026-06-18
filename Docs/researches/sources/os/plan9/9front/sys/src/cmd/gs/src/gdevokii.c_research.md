# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevokii.c

## Role

Okidata IBM-compatible 9-pin dot-matrix printer driver.

## Exported Device

- `gs_okiibm_device`, named `okiibm`, 1-bit output.
- Compile-time defaults: `X_DPI` 120 unless overridden, `Y_DPI` 72 unless overridden.
- Supports 60/120/240 horizontal DPI and 72/144 vertical DPI.

## Main Flow

- `okiibm_print_page` builds initialization/end strings and enables unidirectional printing at higher resolutions.
- `okiibm_print_page1` handles raster conversion and printer command output:
  - skips blank lines,
  - emits vertical feed commands with accounting for Okidata’s 1/216-to-1/144 scaling behavior,
  - copies scan-line blocks,
  - shuffles scan lines for high vertical resolution,
  - transposes 8x8 pixel blocks with `gdev_prn_transpose_8x8`,
  - strips trailing zero columns,
  - emits graphics runs, potentially in multi-pass mode.
- `okiibm_output_run` sends one graphics command and optionally writes all, even, or odd columns depending on pass.

## Device-Specific Notes

The code models the printer’s unusual vertical feed scaling and assumes a power-on initial state for feed accounting.

## Risks and Edge Cases

- `graphics_modes_9[x_dpi / 60]` relies on supported DPI values.
- High-resolution output uses multiple passes and unidirectional mode to improve quality.
- Like other dot-matrix drivers, output is raw printer escape/control byte streams.
