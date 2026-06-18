# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrdp.h

## Role

`gscrdp.h` declares the interface and encoded dictionary format for device-specified Ghostscript CIE CRDs.

This is device parameter/color-management API infrastructure, not filesystem code.

## Public API

- `param_write_cie_render1`
- `param_put_cie_render1`
- `gs_cie_render1_param_initialize`
- `param_get_cie_render1`

## Encoded Format

Defines `GX_DEVICE_CRD1_TYPE` as `101` and documents a modified ColorRenderingType 1 dictionary format:

- `TransformPQRName`
- `TransformPQRData`
- `EncodeLMNValues`
- `EncodeABCValues`
- `RenderTableSize`
- `RenderTableTable`
- `RenderTableTValues`

## Dependencies

Includes `gscie.h` and `gsparam.h`; forward-declares `gx_device`.

## Notable Risks

The header explicitly says the representation is subject to change without notice, so external clients should treat it as internal device-parameter protocol rather than a stable file format.
