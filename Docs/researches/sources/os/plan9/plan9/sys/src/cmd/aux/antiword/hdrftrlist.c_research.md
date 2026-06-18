# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/hdrftrlist.c

Builds and owns per-section header/footer metadata.

Data model:

- Each section has six slots:
  - even header,
  - odd header,
  - even footer,
  - odd footer,
  - first-page header,
  - first-page footer.
- Private `hdrftr_local_type` stores exported `hdrftr_block_type`, character-position range, usefulness flag, and ownership flag for text lists.

Key functions:

- `vDestroyHdrFtrInfoList()` frees only original header/footer output chains, avoiding double-free when entries inherit text from another slot/section.
- `vCreat8HdrFtrInfoList()` builds section records from Word 8+ character position arrays.
- `vCreat6HdrFtrInfoList()` builds Word 6/7 records using DOP/SEP header-footer specification bits.
- `vCreat2HdrFtrInfoList()` reuses the Word 6 path.
- `pGetHdrFtrInfo()` selects the correct slot for section, header/footer, odd/even page, and first-page state.
- `lComputeHdrFtrHeight()` estimates vertical height by scanning output tokens and paragraph/line terminators.
- `vPrepareHdrFtrText()` decrypts header/footer text ranges, computes heights, marks useful records, and applies inheritance from first-page records and previous sections.

This module links file-position parsing to page-layout output. It relies on document property accessors and `pHdrFtrDecryptor()`.
