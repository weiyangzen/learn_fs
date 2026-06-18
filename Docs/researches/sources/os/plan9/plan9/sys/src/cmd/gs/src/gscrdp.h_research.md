# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrdp.h

## Purpose
Interface for device-specified CIE Color Rendering Dictionaries.

## Key Contents
- Declares CRD parameter write APIs:
  - `param_write_cie_render1`,
  - `param_put_cie_render1`.
- Declares CRD parameter read APIs:
  - `gs_cie_render1_param_initialize`,
  - `param_get_cie_render1`.
- Defines `GX_DEVICE_CRD1_TYPE` as 101.
- Documents the modified PostScript-style CRD dictionary representation used for device parameters.

## Important Details
- Documents `TransformPQRName`/`TransformPQRData` instead of raw TransformPQR procedures.
- Documents sampled array representations for EncodeLMN/ABC and RenderTable.T.
- Notes the representation is subject to change.

## Dependencies
Includes `gscie.h` and `gsparam.h`; forward-declares `gx_device`.

## Research Notes
Implementation is in `gscrdp.c`.
