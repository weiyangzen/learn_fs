# sources/sync-backup/rsync/rounding.c

Purpose: Compile-time helper used to validate structure padding assumptions for `rounding.h` generation/build correctness.

Important APIs, types, and functions: Defines `struct test` containing `union file_extras extras[EXTRA_ROUNDING+1]` followed by `int64 test`. `main()` declares a static array sized to fail compilation if `ACTUAL_SIZE != EXPECTED_SIZE`.

Control flow: There is no runtime logic beyond returning success. The important behavior is compile-time array size validation.

State and persistence behavior: No persistent state. It validates compiler layout behavior for rsync's packed file-extra allocation model.

Dependencies and integration points: Includes `rsync.h` for `EXTRA_ROUNDING`, `union file_extras`, and `int64`. Used by the build system as a pre-compilation/helper check.

Risks and test signals: Risk is silent ABI/layout mismatch in file-list extras if this check is bypassed. The test signal is successful compilation; failure indicates padding/alignment assumptions need adjustment.
