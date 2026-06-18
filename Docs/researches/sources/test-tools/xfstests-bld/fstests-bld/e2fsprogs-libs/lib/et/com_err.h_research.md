# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/com_err.h

## Purpose
`com_err.h` is the public API header for the com_err library and its Kerberos/Heimdal compatibility surface.

## Important APIs, Types, and Functions
It defines `errcode_t`, `struct error_table`, forward-declares `struct et_list`, and declares `com_err()`, `com_err_va()`, `error_message()`, hook functions, `init_error_table()`, `add_error_table()`, `remove_error_table()`, `add_to_error_table()`, `com_right()` variants, `initialize_error_table_r()`, `free_error_table()`, and list lock helpers.

## Control Flow
There is no runtime control flow; the header fixes ABI signatures and format attributes for compile-time checking.

## State, Persistence, Dependencies, Risks, and Test Signals
State is represented by global hook and error-table declarations. Dependencies are stddef, stdarg, compiler attribute support, and matching implementations in `com_err.c`, `error_message.c`, `init_et.c`, and `com_right.c`. Risks include ABI drift across com_err implementations and exposing incomplete `et_list` for compatibility. Test signals are successful builds of generated error tables and users of both MIT and Heimdal APIs.
