# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcrd.c

Implements Level 2 CIE Color Rendering Dictionary support.

Primary operators expose current CRD state, build ColorRenderingType 1 CRDs, build device CRDs, and install CRDs into the graphics state: `currentcolorrendering`, `.buildcolorrendering1`, `.builddevicecolorrendering1`, `.setcolorrendering1`, and `.setdevicecolorrendering1`.

`zcrd1_params()` extracts dictionary parameters such as `MatrixLMN`, `RangeLMN`, `MatrixABC`, `RangeABC`, white/black points, `MatrixPQR`, `RangePQR`, and optional `RenderTable`. `zcrd1_proc_params()` extracts executable procedures including `EncodeLMN`, `EncodeABC`, `TransformPQR`, and render-table transform procedures.

The file schedules cache construction on the execution stack. `cache_colorrendering1()` prepares sampled caches for encoding functions and render-table transforms, while `cie_cache_render_finish()` converts caches and completes the CRD.

`cie_cache_joint()` builds joint TransformPQR caches between the active CIE color space and CRD. It constructs temporary executable arrays that shuffle operands through `cie_exec_tpqr()` and cleanup through `cie_tpqr_finish()`.

Includes optimized C implementations of default white/black scaling procedures: `.TransformPQR_scale_WB0`, `.TransformPQR_scale_WB1`, and `.TransformPQR_scale_WB2`.

Notable risk areas: several comments flag reference-count fixes; cache building depends on correct estack unwinding; driver-provided CRDs use null procedure refs and bypass PostScript procedure sampling.
