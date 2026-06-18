<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ImageAndTextCell.m -->
# sources/sync-backup/unison/src/uimac/ImageAndTextCell.m

Source read: complete file, 130 lines, 5359 bytes, sha256 `ef0be26e27272c67`.

Purpose: Implements combined icon/text cell rendering for older AppKit table views.

Important APIs/types/functions: Overrides `copyWithZone:`, `dealloc`, `editWithFrame:...`, `selectWithFrame:...`, `drawWithFrame:inView:`, and `cellSize`; adds private `imageFrameForCellFrame:`.

Implementation inventory: discovered Objective-C/C callback methods include `dealloc, setImage, image, imageFrameForCellFrame, editWithFrame, selectWithFrame, drawWithFrame, cellSize`.

Control flow: Drawing reserves `3 + image.width` points at the leading edge, fills image background if needed, vertically centers the image with flipped-view handling, composites it, then delegates text drawing to `NSTextFieldCell`. Editing and selection use the same split so the text editor does not overlap the image.

State and persistence behavior: Owns a retained image pointer. No persistent state or caches are maintained.

Dependencies and integration points: Depends on AppKit image compositing APIs including older `NSCompositeSourceOver`; integrates with table display code in `MyController`.

Risks: The file contains old Apple license text with a mojibake copyright character. Deprecated compositing APIs may warn or fail on modern SDKs. `setStatus`-style retain/release is correct here, but frame math assumes non-nil image in edit/select paths.

Test signals: Table visual smoke tests with folder/file icons, selected rows, flipped views, and empty images. Compile on the target macOS SDK to catch deprecated API errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ImageAndTextCell.m -->
