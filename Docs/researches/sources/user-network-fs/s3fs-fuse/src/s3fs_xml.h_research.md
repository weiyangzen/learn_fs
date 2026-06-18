# sources/user-network-fs/s3fs-fuse/src/s3fs_xml.h

Purpose: declares XML helper functions and libxml smart-pointer aliases, plus the parser-error buffer utility used when reading XML from memory.

Important APIs and types: `S3FS_XML_PARSE_FLAGS` disables external entity/network behavior where possible. `unique_ptr_xmlChar`, `unique_ptr_xmlXPathObject`, `unique_ptr_xmlXPathContext`, and `unique_ptr_xmlDoc` encode libxml cleanup ownership. `s3fsXmlBufferParserError` installs a generic error handler into a fixed buffer. Public functions include truncation/token extraction, object appending, incomplete MPU parsing, and `simple_parse_xml`.

Control flow: callers parse XML with libxml and use these functions to query known S3 response shapes. The parser-error helper is set immediately before `xmlReadMemory` and inspected after parse failure.

State and persistence: aliases own libxml allocations through custom deleters. The error helper owns a 1024-byte stack/member buffer, but the libxml generic error hook it installs is global.

Dependencies and integration points: includes libxml parser/xpath headers, `mpu_util.h`, and forward-declares `S3ObjList`. Used by request and utility-mode code.

Risks: `xmlSetGenericErrorFunc` is global and can race with concurrent XML parsing. The fixed error buffer truncates long parser diagnostics. Header includes `<cstring>` and writes parser handler inline, so changes can affect many translation units.

Test signals: parser flag verification for XXE-blocking behavior, malformed XML diagnostic capture, smart-pointer cleanup under sanitizers, and concurrent parse tests if XML parsing happens from multiple request threads.
