# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrd.h

## Role

`gscrd.h` declares the public interface for creating and initializing Ghostscript CIE Color Rendering Dictionaries.

This is color-management API infrastructure, not filesystem code.

## Public API

- `gs_cie_render1_build`
- `gs_cie_render1_init_from`
- `gs_cie_render1_initialize`
- `gs_cie_render_client_data`

## Important Contracts

The header documents that `gs_cie_render1_build` returns a CRD with reference count 1, while `gs_setcolorrendering` increments it again. Clients should decrement their reference after setting the CRD if they do not intend to keep it.

`gs_cie_render1_init_from` copies scalar/matrix/range/procedure values but only copies the render-table pointer, not the render-table data.

## Dependencies

Includes `gscie.h`.

## Notable Risks

Render-table data lifetime remains caller-owned or externally managed; the initializer does not deep-copy it.
