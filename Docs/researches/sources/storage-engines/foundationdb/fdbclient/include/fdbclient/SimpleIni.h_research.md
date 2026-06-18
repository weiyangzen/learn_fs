# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SimpleIni.h

## Purpose
`SimpleIni.h` is a vendored single-header INI parser/writer, version 4.16, used for cross-platform configuration file loading and saving. It supports comments, sections, key/value pairs, optional duplicate keys, optional multiline values, load-order-preserving save, UTF-8/MBCS/wide-character conversion, file/string/stream I/O, and case-sensitive or case-insensitive lookup.

## Important APIs, Types, And Functions
- `SI_Error` reports success, update/insert outcomes, generic failure, allocation failure, and file errors.
- `CSimpleIniTempl<SI_CHAR, SI_STRLESS, SI_CONVERTER>` is the main template.
- Nested `Entry` stores item pointer, comment pointer, and load order, with `KeyOrder` and `LoadOrder` comparators.
- `TKeyVal`, `TSection`, and `TNamesDepend` represent section/key/value maps and pointer-returning name lists.
- `OutputWriter`, `FileWriter`, `StringWriter`, and optional `StreamWriter` abstract saving.
- `Converter` wraps the selected conversion backend and grows scratch space for output conversion.
- Public settings include `SetUnicode`, `SetMultiKey`, `SetMultiLine`, and `SetSpaces`.
- Loading APIs include `LoadFile()` for narrow/wide filenames, `FILE*`, optional `istream`, string, and raw memory.
- Saving APIs include `SaveFile()`, `Save(OutputWriter&)`, optional `ostream`, and string append.
- Query/mutation APIs include `GetAllSections`, `GetAllKeys`, `GetAllValues`, `GetSectionSize`, `GetSection`, `GetValue`, typed long/double/bool getters and setters, `SetValue`, and `Delete`.
- Conversion helpers include generic case comparators, `SI_ConvertA`, and wide conversion backends for generic ConvertUTF, ICU, and Win32.
- Typedefs provide `CSimpleIniA`, `CSimpleIniCaseA`, `CSimpleIniW`, `CSimpleIniCaseW`, and `CSimpleIni`.

## Control Flow And State
`LoadFile()` reads the whole file into a byte buffer and calls `LoadData()`. `LoadData()` strips UTF-8 BOM when needed, converts storage encoding to `SI_CHAR`, then mutates the converted buffer in place by inserting NUL terminators while `FindFileComment()` and `FindEntry()` parse comments, sections, keys, values, and multiline blocks. `AddEntry()` inserts or updates maps, copies strings when data is appended after an existing load, tracks load order, and handles multikey replacement. `Save()` sorts sections/keys by load order, writes comments, sections, key/value lines, and emits multiline data with `<<<END_OF_TEXT`. `Delete()` removes keys or sections and frees copied strings.

## Persistence And External State
The parser owns a mutable data block `m_pData`, copied strings in `m_strings`, file comment pointer, parsed map, encoding/multikey/multiline/spacing flags, and load-order counter. Saved output persists to files, streams, or strings. Returned pointers from query methods depend on `CSimpleIniTempl` lifetime and are invalidated by reset or deletion.

## Dependencies And Integration Points
The header depends on STL containers, C stdio/string functions, optional iostreams, platform conversion APIs, ICU if enabled, and FoundationDB's `ConvertUTF.h` for generic wide conversion. It is a third-party component embedded in fdbclient for INI-style configuration needs.

## Risks And Edge Cases
The parser mutates the load buffer in place and returns dependent pointers, so ownership/lifetime misuse is the largest risk. Duplicate-key behavior changes depending on `m_bAllowMultiKey`. Comments can only be changed by deleting and recreating entries. Multiline parsing requires exact tag placement and normalizes newlines. Case-insensitive comparison is ASCII-generic except for Win32 MBCS mode. Some code uses fixed-size buffers for numeric conversion and wide filename conversion. `DeleteString()` compares pointers against `m_pData`, which assumes all dependent strings belong either to the main block or `m_strings`.

## Test Signals
Tests should cover narrow and UTF-8 files with BOM, comments before file/section/key, key/value whitespace trimming, invalid lines, empty sections, duplicate keys in both modes, force replacement preserving order/comment, multiline load/save, save order, typed numeric/bool getters and setters, deletion and empty-section pruning, string/file/stream I/O, case-sensitive and insensitive typedefs, reset memory ownership, and conversion backends on supported platforms.
