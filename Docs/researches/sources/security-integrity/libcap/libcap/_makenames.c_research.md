## sources/security-integrity/libcap/libcap/_makenames.c

Purpose: build-time generator that turns `cap_names.list.h` into `cap_names.h`, defining capability count, maximum name size, and optional name array.

Important APIs/functions: generated `list[]`, helper `recalloc()`, and `main()`.

Control flow: scans list entries to find highest capability index and longest name, grows a sparse pointer array, emits a generated-file header, `__CAP_BITS`, `__CAP_NAME_SIZE`, and `LIBCAP_CAP_NAMES` array with `NULL` placeholders for unused indices.

State/persistence: writes generated C preprocessor output to stdout; Makefile redirects to `cap_names.h`.

Dependencies/integration: `cap_names.list.h` generated from UAPI header, C build compiler, libcap internal `cap_text.c` and `libcap.h`.

Risks: `recalloc` uses int byte counts and assumes growth sizes are small; malformed duplicate indices overwrite earlier names silently.

Test signals: `make -C libcap cap_names.h`, compile `cap_text.o`, and `go/Makefile` `good-names.go` diff.
