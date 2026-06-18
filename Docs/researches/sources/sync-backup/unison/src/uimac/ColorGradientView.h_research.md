<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ColorGradientView.h -->
# sources/sync-backup/unison/src/uimac/ColorGradientView.h

Source read: complete file, 22 lines, 456 bytes, sha256 `487fcd00abedb20f`.

Purpose: Declares a small `NSView` subclass used by the Unison Mac UI to paint gradient backgrounds behind connection/status/detail regions.

Important APIs/types/functions: Exports retained `startingColor` and `endingColor` properties plus an assign `angle` property. The public contract is intentionally just configurable colors and gradient direction.

Control flow: The implementation initializes defaults and draws the gradient during AppKit `drawRect:` callbacks. Interface Builder can bind outlets to this class and set properties through Objective-C accessors.

State and persistence behavior: State is per-view retained color objects and an integer angle. There is no persistence beyond nib/runtime view state.

Dependencies and integration points: Depends on Cocoa/AppKit and `NSGradient` behavior in the implementation. It is referenced by `MyController` outlets for the connection and details views.

Risks: Manual retain semantics mean missing release/dealloc would leak in long-lived nib reloads. Nil `startingColor` would make the fill path unsafe if set externally.

Test signals: Instantiate from the nib and programmatically, set equal and different colors, and snapshot the connection/details panels for solid-fill and gradient cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ColorGradientView.h -->
