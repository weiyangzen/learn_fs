<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ImageAndTextCell.h -->
# sources/sync-backup/unison/src/uimac/ImageAndTextCell.h

Source read: complete file, 20 lines, 349 bytes, sha256 `8152461ef119cb2c`.

Purpose: Declares an Apple sample-derived `NSTextFieldCell` subclass that displays an icon and text in the same outline/table cell.

Important APIs/types/functions: `setImage:`, `image`, `drawWithFrame:inView:`, and `cellSize` are the main surface used by the reconcile table's path/change columns.

Implementation inventory: discovered Objective-C/C callback methods include `setImage, image, drawWithFrame, cellSize`.

Control flow: Controllers set an image on the cell before display; the implementation divides the cell frame into image and text regions for drawing, editing, and selection.

State and persistence behavior: The cell stores one retained `NSImage`. Copied cells retain the same image reference.

Dependencies and integration points: Depends on Cocoa `NSTextFieldCell` and is used from `MyController` while displaying `ReconItem` objects.

Risks: Manual memory management and inherited cell copying must keep image ownership correct. Image width affects editing/selection frame math.

Test signals: Render rows with and without images, copy cells through table reuse, and edit/select text to ensure the editor starts after the icon.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/ImageAndTextCell.h -->
