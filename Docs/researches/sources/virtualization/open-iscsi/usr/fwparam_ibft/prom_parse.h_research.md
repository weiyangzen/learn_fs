# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.h

Shared parser/lexer interface header for the firmware parameter parser. It includes standard allocation/string headers and `iscsi_obp.h`, forward-declares `struct ofw_dev`, and exposes `yyerror`, `yylex`, `yyin`, `yytext`, `yyleng`, and `yydebug`.

The header includes the generated Bison interface `prom_parse.tab.h`, which defines token numbers, semantic value storage, location type, and `yyparse(struct ofw_dev *ofwdev)`.

`YY_NO_UNPUT` is defined to match the Flex scanner configuration. This keeps the generated scanner/parser interface consistent and avoids expecting Flex `unput` support.
