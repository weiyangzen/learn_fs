# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/hdrftrlist.c

This file builds and prepares per-section Word header/footer records.

Key routines:
- `vDestroyHdrFtrInfoList()` frees generated header/footer text only where the record owns the text.
- `vCreat8HdrFtrInfoList(...)` maps Word 8+ character position arrays into six header/footer slots per section.
- `vCreat6HdrFtrInfoList(...)` maps Word 6/7 header/footer positions using DOP/SEP specification bits.
- `vCreat2HdrFtrInfoList(...)` delegates to the Word 6/7 creator.
- `pGetHdrFtrInfo(...)` returns the appropriate header/footer record for section, header/footer kind, odd/even page, and first-page status.
- `vPrepareHdrFtrText(...)` extracts header/footer text, computes rendered height, marks usefulness, and applies inheritance.

Important behavior:
- Six slots are tracked: even header, odd header, even footer, odd footer, first-page header, first-page footer.
- Inheritance fills missing odd/even records from first-page records in the first section, and from previous sections thereafter.
- `bTextOriginal` prevents double-free when inherited records share text pointers.

Dependencies:
- Section metadata, DOP/SEP header/footer flags, header/footer decryptor, output linked lists, font leading and unit conversion helpers.

Role in antiword:
- Supplies resolved header/footer content and height for page layout.
