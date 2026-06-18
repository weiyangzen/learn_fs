# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/textgen.c

Text-object generation for Plan 9 `pic`.

Key responsibilities:
- Builds `TEXT` objects from accumulated attributes and text strings.
- Applies height, width, invisibility, placement, and `with` anchoring attributes.
- Updates current drawing position according to text size and global direction.
- Stores text fragments in the growing global `text` array.
- Wraps raw troff command strings as `TROFF` nodes.

Important behavior:
- Default height is `textht * number_of_text_strings` unless height is explicitly set.
- `WITH` adjusts current position so the requested anchor lies at the current point.
- Text extents are reported through `extreme()` before returning the node.
- Isolated text modifiers rewrite the last saved text item’s type.

Dependencies:
- Uses parser globals `attr`, `nattr`, `text`, `ntext`, `curx`, `cury`, `hvmode`, and helpers such as `getfval`, `grow`, `makenode`, `isright`, `isleft`, and `isup`.

Notable risks:
- Assumes isolated `TEXTATTR` modifiers have a previous text entry to modify.
- Static `prevh` and `prevw` are assigned but unused in this file.
