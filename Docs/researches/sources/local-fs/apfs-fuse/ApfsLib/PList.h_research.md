# File Research: sources/local-fs/apfs-fuse/ApfsLib/PList.h

This header declares the plist object hierarchy and the XML parser interface. The supported plist types are integer, string, data, array, and dictionary.

`PLObject` is an abstract base with a virtual `type()` and typed downcast helpers. `PLInteger`, `PLString`, and `PLData` store scalar values. `PLArray` owns a vector of raw `PLObject*` children, and `PLDict` owns a map from strings to raw `PLObject*` values. Destructors in the `.cpp` perform deletion, so callers must respect ownership boundaries.

`PListXmlParser` is a single-pass parser over a caller-provided memory buffer. It exposes `Parse()` and privately implements array/dict/object parsing, base64 decoding, tag scanning, content extraction, and byte-wise character reads.

The `PList` wrapper class is declared but marked “Not used ... maybe later, if we need bplists ...”. Its XML parse method is not functional in the implementation. There is no binary plist parser here.
