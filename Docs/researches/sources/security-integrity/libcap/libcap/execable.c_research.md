## sources/security-integrity/libcap/libcap/execable.c

Purpose: executable entry body embedded in `libcap.so` so the shared library can print version/help/summary when run directly.

Important APIs/functions: `usage()`, `summary()`, and `SO_MAIN` from `execable.h`. Uses `cap_max_bits`, `cap_get_mode`, `cap_mode_name`, `cap_to_name`, and `cap_free`.

Control flow: prints library version/license/homepage, handles `--usage`/`--help` by printing usage, handles `--summary` by reporting current mode and comparing libcap-known capabilities with running-kernel supported capabilities.

State/persistence: reads process capability mode and kernel bounds; no persistent writes.

Dependencies/integration: compiled with `LIBRARY_VERSION` and `SHARED_LOADER`, included into shared-lib magic object by `libcap/Makefile`.

Risks: executable shared-library behavior is loader/linker sensitive; summary depends on runtime kernel capability count.

Test signals: `./libcap.so`, `./libcap.so --usage`, `./libcap.so --help`, and `./libcap.so --summary` from `libcapsotest`.
