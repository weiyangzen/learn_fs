# sources/test-tools/syzkaller/prog/heatmap_test.go

Purpose: validates generic heatmap segment selection and index translation.

Important APIs/types/functions: `TestGenericHeatmap`, `checkIndex`, `region`, and `GenericHeatmap.debugPrint`.

Control flow and state: test cases provide base64-encoded data and allowed raw regions. The test decodes data, builds heatmaps over many iterations, samples locations, and fails with debug dumps if any selected index falls outside allowed regions. An all-constant input verifies fallback to uniform full-data coverage.

Dependencies and integration: uses `pkg/image.DecodeB64`, `pkg/testutil` iteration/rand helpers, and private heatmap internals for debug output.

Risks: probabilistic sampling may not exercise every segment boundary each run, but any invalid selected region is caught. Expected regions are tied to current `granularity`.

Test signals: confirms sparse non-constant segment detection, all-constant fallback, raw bounds checking, and debug visibility for failed segment maps.
