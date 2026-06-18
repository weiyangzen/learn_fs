## sources/storage-engines/wiredtiger/src/utilities/util_cpyright.c

Purpose: implements the `wt copyright` command by printing licensing and contact text.

Important APIs/types/functions: the single function `util_copyright` emits fixed strings to stdout using `printf`. It has no arguments and no return code.

Control flow: straight-line output of copyright, GPL notice, warranty disclaimer, GPL URL, and MongoDB contact text. Dispatch in `util_main.c` calls it directly and exits without opening a database.

State and persistence behavior: no database, filesystem, or process-global state is modified except stdout.

Dependencies and integration points: included in the utility build and dispatched by the `copyright` command case. It depends only on the C runtime and `util.h`.

Risks: text can drift from actual licensing policy or current copyright years. Since it prints directly, output errors are not checked and cannot influence exit status.

Test signals: `wt copyright` should run without a database home and print the expected stable notice. Packaging/legal review is the meaningful non-code validation signal.
