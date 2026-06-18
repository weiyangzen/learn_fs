# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_lex.l

Hand-authored Flex lexer for parsing Open Firmware boot paths and OBP iSCSI boot arguments. It feeds tokens and string values to the Bison parser declared through `prom_parse.h`.

The lexer defines token regexes for Open Firmware device paths: bus names (`ata`, `pci`, `scsi`, `usb`, and others), boot devices (`disk`, `cdrom`, `ethernet`, `iscsi-diskN`, `iscsi-toe`, `sd`), CHOSEN boot properties, OBP qualifiers (`bootp`, `ipv6`, `iscsi`, `dhcpv6`), OBP parameters such as CHAP fields and target identifiers, IPv4 literals, IQNs, hex chunks, and escaped filenames.

The `upval(d)` macro is the central action: it copies matched text into `yylval.str`, updates parser location columns, and returns the token kind. Whitespace is skipped with location updates. All other single characters are returned as literal grammar tokens.

The lexer is non-interactive, has no `yywrap`, disables `input` and `unput`, and uses array-backed `yytext`. It is tightly coupled to `prom_parse.y` token names and to `YYSTYPE.str`.
