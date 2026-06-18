# sources/test-tools/strace/maint/enum2xlat.sh

Purpose: generates strace xlat `.in` tables from C enum definitions in a source header, either listing enum names or writing table content.

Important APIs/types/functions: shell functions `print_help`, `print_usage`, and `gen`; options `-d DIR`, `--list`, `--stdout`; sed extraction of `enum NAME { ... };`; filtering of `_MAX` members; optional `#value_indexed` directive when enum values are implicit.

Control flow: parse options, validate mode/arguments, verify the input file is readable, default enum list from `sed` if no enum names are supplied, then either print enum names, print generated content to stdout, or write each table to `src/xlat/<enum>.in`.

State and persistence behavior: writes generated xlat files under the selected directory unless `--stdout` is used. It does not use temporary files, so interrupted writes can leave partial `.in` files.

Dependencies and integration points: consumed by xlat maintenance and by `update-xlat.sh`, which reconstructs commands from generated headers. The generated files feed `src/xlat/Makemodule.am` and decoder constant tables.

Risks: enum parsing is line-oriented and uppercase-name oriented; comments, explicit complex values, multiline names, or lowercase constants can be skipped. `eval` users downstream rely on the generated header line remaining stable.

Test signals: `--list` should enumerate expected enums; `--stdout` diffs should match checked-in xlat tables; xlat generation and decoder builds should continue to compile.
