# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdu.c

## Purpose
Provides shared PostScript/PDF writer utilities for vector state emission, color setting, binary data stream setup, DCT/CCITT filter setup, unsupported readback stubs, and overprint compositor handling.

## Key Behavior
- Defines GC descriptors for `gx_device_psdf` and `psdf_binary_writer`.
- Provides standard fill and stroke color command names for PDF/PostScript-like color operators.
- Emits vector graphics state operations:
  - line width, cap, join, miter limit,
  - dash pattern,
  - flatness,
  - rectangles and path operators.
- Implements `psdf_set_color`, including compact gray/RGB/CMYK output and adjustment for the `gx_no_color_index` sentinel collision.
- Implements `psdf_round` and byte-color rounding for compact numeric output.
- Implements `psdf_begin_binary`, optionally wrapping output in ASCII85 when binary output is disabled.
- Adds arbitrary stream filters through `psdf_encode_binary`.
- Builds DCTEncode state through `psdf_DCT_filter`, injecting `Rows`, `Columns`, and `Colors`, allocating JPEG compression data, and ensuring scan-line/user-marker buffer sizing.
- Builds CCITTFaxEncode state through `psdf_CFE_binary`.
- Closes binary filter chains through `psdf_end_binary`.
- Rejects `get_bits` / `get_bits_rectangle` for high-level vector devices.
- Treats overprint compositors as natively supported and otherwise delegates compositor creation to the default device.

## Dependencies
Uses vector-device APIs, stream filter APIs, ASCII85, CCITT Fax, DCT/JPEG, PostScript string writing, and overprint compositor helpers.

## Research Notes
Logical-operation output is effectively ignored except for a comment noting that set-0/set-1 should be detected. Many output functions do not check stream error status locally; callers that require hard I/O error propagation must rely on later stream/file checks.
