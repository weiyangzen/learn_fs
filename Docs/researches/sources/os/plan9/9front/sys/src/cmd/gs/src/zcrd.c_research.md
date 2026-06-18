# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcrd.c

Implements CIE color rendering dictionary operators and cache setup.

Key behavior:
- Provides `currentcolorrendering`, `.buildcolorrendering1`, `.builddevicecolorrendering1`, `.setcolorrendering1`, and `.setdevicecolorrendering1`.
- Validates ColorRenderingType 1 dictionaries, procedure entries, matrices, ranges, white/black points, and optional RenderTable data.
- Builds `gs_cie_render` objects, installs them into interpreter state, and caches EncodeLMN, EncodeABC, RenderTableT, and TransformPQR computations.
- Uses continuation operators to sample PostScript procedures into C-side CIE caches.
- Includes C implementations of default relative-colorimetric `TransformPQR_scale_WB[0-2]`.

Dependencies:
- Depends on CIE rendering/color-space internals, dictionary parameter helpers, interpreter memory, and e-stack cache continuations.

Research notes:
- Most complexity is asynchronous cache loading: failures must restore `esp` and free partially built rendering objects.
