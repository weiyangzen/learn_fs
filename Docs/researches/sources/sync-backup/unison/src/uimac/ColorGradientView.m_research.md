<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ColorGradientView.m -->
# sources/sync-backup/unison/src/uimac/ColorGradientView.m

Source read: complete file, 46 lines, 1220 bytes, sha256 `b52d55aa12c63e99`.

Purpose: Implements `ColorGradientView`, drawing either a solid background or an `NSGradient` over the view bounds.

Important APIs/types/functions: Uses synthesized `startingColor`, `endingColor`, and `angle`. `initWithFrame:` sets grid/control-shadow defaults and `drawRect:` performs the render.

Implementation inventory: discovered Objective-C/C callback methods include `initWithFrame, drawRect`.

Control flow: When AppKit asks the view to draw, equal or nil ending colors trigger a plain `NSRectFill`; otherwise the method allocates an `NSGradient`, draws it over `[self bounds]` at `angle`, and releases it.

State and persistence behavior: Only the three properties affect rendering. Drawing is stateless aside from retained colors, and no backing cache is kept.

Dependencies and integration points: Depends on AppKit color and gradient classes and on nib/controller code that embeds the view.

Risks: The class lacks an explicit `dealloc` for retained synthesized properties in manual reference counting. `drawRect:` ignores the dirty `rect` and redraws full bounds, which is simple but less efficient.

Test signals: Verify no crash with default initialization, equal colors, and changed colors. Run under leaks/static analyzer to catch retained property cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ColorGradientView.m -->
