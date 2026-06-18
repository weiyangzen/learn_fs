# sources/storage-engines/badger/.trunk/configs/svgo.config.mjs

Purpose: configures SVGO optimization for SVG assets under Trunk.

Important data: exports an ES module config using `preset-default`, overriding `removeViewBox: false`, `sortAttrs: true`, and `removeOffCanvasPaths: true`. Keeping `viewBox` preserves SVG scalability, while sorting attributes stabilizes diffs.

State and persistence: affects formatted/optimized SVG output, not application runtime unless SVGs are regenerated. Dependencies are SVGO v4 via Trunk. Risks: removing off-canvas paths can change intentionally hidden or clipped SVG content; retaining viewBox avoids a common rendering regression. Test signals are SVGO lint/format results and visual review of changed SVG assets.
