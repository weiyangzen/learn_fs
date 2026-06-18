# sources/sync-backup/rsync/itypes.h

Purpose: defines small inline wrappers around `<ctype.h>` classification/conversion macros that safely cast through `unsigned char`, avoiding undefined behavior for negative `char` values.

Important APIs/types/functions: `isDigit`, `isHexDigit`, `isPrint`, `isSpace`, `isAlNum`, `isLower`, `isUpper`, `toLower`, and `toUpper`. Each accepts a `const char *` and applies the corresponding C library macro/function to the pointed byte.

Control flow: each helper is a single inline return statement. The pointer form lets calling code pass a cursor into a string without manually casting the dereferenced byte.

State and persistence behavior: no state and no persistence. Behavior depends on the active C locale for the underlying ctype functions, so classification can be locale-sensitive outside the ASCII range.

Dependencies/integration: included by general rsync parsing and formatting code, including numeric formatting in `compat.c`. It relies on `rsync.h` or surrounding includes to provide ctype declarations and integer typedefs.

Risks/test signals: callers must pass a valid pointer; there is no null or bounds check. Tests should include bytes with the high bit set on platforms where plain `char` is signed, and should consider locale-sensitive behavior if rsync expects ASCII-only parsing in a path.
