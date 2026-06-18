# sources/user-network-fs/nfs-utils/support/junction/xml.c

## Purpose
Provides libxml2 helper functions for junction XML attribute/content conversion and xattr-backed XML parse/write.

## Important APIs, Types, and Functions
Includes `junction_xml_is_empty()`, node name/find helpers, bool/u8/int attribute getters/setters, int content getters/setters, `junction_xml_parse()`, and `junction_xml_write()`.

## Control Flow
Parse opens the junction directory, reads the xattr into memory, and calls `xmlReadMemory()`. Write opens the directory, dumps the XML document as formatted UTF-8 memory, and stores it as a trusted xattr. Attribute helpers convert strings with strict numeric bounds.

## State and Persistence Behavior
Persistent state is the XML document stored in a trusted xattr. Temporary XML docs/buffers are caller or function owned and freed after use.

## Dependencies and Integration Points
Depends on libxml2 and `junction.c` xattr helpers. Used by `nfs.c` for NFS junction serialization.

## Risks and Edge Cases
XML parser uses default libxml flags, so parser hardening should be reviewed for untrusted xattr content. Logging line in parse read formats buffer oddly. Numeric conversion rejects trailing characters.

## Test Signals
Test bool/int/u8 parse success/failure, missing attributes, XML xattr round trips, malformed XML, large xattrs, and write failures.
