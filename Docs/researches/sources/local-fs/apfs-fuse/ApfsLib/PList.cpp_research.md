# File Research: sources/local-fs/apfs-fuse/ApfsLib/PList.cpp

This file implements a small XML property-list object model and parser. It defines runtime type checks for `PLObject`, concrete plist types for integer/string/data/array/dict, destructors that delete owned child objects, and a hand-written XML plist parser.

`PLObject::toInt()`, `toString()`, `toData()`, `toArray()`, and `toDict()` use `dynamic_cast` to safely downcast. Each concrete type returns its enum value through `type()` and exposes stored values through accessors declared in the header.

`PListXmlParser::Parse()` scans tags until it finds `<plist>`, then calls `ParseObject()` for the root. Parse errors are caught as `PLException`, printed to stderr, and return `nullptr`. Processing instructions and doctypes are recognized by `FindTag()` but not semantically processed.

`ParseArray()` repeatedly parses child objects until `ParseObject()` returns `nullptr`, which happens when an end tag is encountered. `ParseDict()` expects alternating `<key>text</key>` and object values until `</dict>`. It rejects empty keys and unexpected tags. `ParseObject()` handles integer, string, data, array, dict, and empty `<true/>`/`<false/>` tags. Booleans are represented as `PLInteger` values 1 and 0.

`Base64Decode()` decodes plist `<data>` contents while ignoring non-base64 whitespace and stopping at `=` padding. It pushes bytes after 2, 3, and 4 base64 characters.

`FindTag()` is a minimal tag scanner. It identifies start/end/empty/proc-instr/doctype tags and captures the tag name up to whitespace, slash, or `>`. It does not implement full XML parsing, attributes beyond skipping them, entity decoding, comments, CDATA, or robust malformed-input recovery.

At the end, the wrapper class `PList::parseXML()` is currently a stub that ignores its arguments and returns false. The usable parser is `PListXmlParser` directly, not the `PList` wrapper.
