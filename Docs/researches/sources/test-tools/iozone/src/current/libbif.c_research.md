# sources/test-tools/iozone/src/current/libbif.c

Purpose: tiny BIFF2 writer used by iozone to create simple Excel-compatible worksheet files containing integer, floating-point, and string cells.

Important APIs/types/functions: public API is `create_xls(char *)`, `close_xls(int)`, `do_int(int,int,int,int)`, `do_float(int,double,int,int)`, and `do_label(int,char *,int,int)` when `HAVE_ANSIC_C` is set, with K&R fallback definitions otherwise. Internal helpers are `do_header`, `do_eof`, and `endian`. BIFF record structs model BOF, integer, label, and float cells, with constants `BOF`, `INTEGER`, `FLOAT`, `LABEL`, `EXCEL_VERS`, and `WORKSHEET`.

Control flow: `create_xls` unlinks the target, opens it, writes a BOF record, and returns the file descriptor. Cell writers construct BIFF records with little-endian row, column, and value fields, then write them directly. `do_float` converts the in-memory double to little-endian byte order for little, big, and one middle-endian layout before writing the fixed header and double separately to avoid structure padding. `do_label` zeroes a 255-byte string array, truncates overlong input by modifying `string[254]`, copies it into the record, and writes the full label struct. `close_xls` writes EOF and closes the descriptor.

State/persistence behavior: each call appends binary BIFF records to the worksheet file. There is no buffering beyond stack structs and no workbook state besides the file descriptor. Existing output files are removed on create. Global `junk` receives write return values but they are not validated.

Dependencies/integration: depends on low-level POSIX/Windows-like `open`, `write`, `close`, and `unlink`, plus platform include branches for AIX/BSD/Linux/macOS/Windows. It integrates with iozone reporting code that wants legacy `.xls` output without an external spreadsheet library.

Risks/test signals: row and column limits are effectively 8-bit/BIFF2 era and comments warn values above 255 behave poorly. `do_label` can mutate the caller's string when truncating and does not re-check writable storage. Writes are unchecked, so disk/full or descriptor failures can silently corrupt output. A test signal is opening generated files in a spreadsheet tool and checking integer, float byte order on big/little endian, labels at expected cells, and EOF presence.
