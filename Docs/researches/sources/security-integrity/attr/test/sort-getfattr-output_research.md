## sources/security-integrity/attr/test/sort-getfattr-output

Purpose: normalize `getfattr` multi-file output for tests.

It reads all input as one string, splits records on blank lines, sorts them, and prints records separated by blank lines. State is stream content only. Dependencies are Perl. Risks are assuming blank-line record separators and potentially reordering meaningful output if a value contains the same separator format. Test signal is stable transcript comparisons across filesystem traversal order.
