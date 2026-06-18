# sources/user-network-fs/samba/source3/intl/linux-msg.sed

## Purpose
`linux-msg.sed` converts Uniforum `.po` translation files into Linux `.msg` message catalog format. It was originally from GNU gettext tooling and assigns monotonically increasing numeric message IDs while emitting translations and original-message comments.

## Important Rules and Behavior
- On the first input line, inserts `$set 1 # Automatically created by po2msg.sed`, initializes hold space, and starts the numeric counter at `0`.
- For each `msgid`, strips the opening `msgid "`, increments the decimal counter in hold space using sed substitutions, and prints a comment line of the form `$ #<id> Original Message:(...)`.
- For each `msgstr`, rewrites the translated string to `# <translation>`, folds continuation lines, inserts trailing backslashes for multi-line translations, and prints catalog text.
- All other lines are deleted with final `d`.

## Control Flow and State
The sed script uses pattern space and hold space as state. Hold space carries the current message ID counter. Labels `:d`, `:b`, and `:a` implement decimal incrementing and multi-line `msgstr` processing. `N`, `P`, `D`, `G`, `x`, and branch-on-substitution commands form the control flow.

## Persistence Behavior
No runtime persistence. It writes generated `.msg` output to stdout for build/install tooling.

## Dependencies and Integration Points
It integrates with Samba's internationalization build process and must be used with the same `.po` ordering as `po-to-tbl` so generated catalog IDs match `cat-id-tbl.c`.

## Risks
- The script assumes simple `.po` syntax and has comments noting that old multi-line `msgid` handling does not work with newer formats.
- Message ordering must remain stable between this conversion and table generation.
- Shell/sed portability matters because the script may run during builds on different Unix variants.

## Test Signals
Builds that regenerate message catalogs, comparison of generated `.msg` IDs against `cat-id-tbl.c`, and sample `.po` files with single-line and multi-line `msgstr` entries.
