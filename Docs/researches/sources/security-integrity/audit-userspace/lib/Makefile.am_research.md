# sources/security-integrity/audit-userspace/lib/Makefile.am

Purpose: Automake build rules for `libaudit.la`, public headers, pkg-config metadata, generated lookup tables, and build-host table generator programs.

Important APIs and targets: Builds `libaudit.la` from `libaudit.c`, `netlink.c`, `lookup_table.c`, `audit_logging.c`, `deprecated.c`, and private headers. Installs `libaudit.h`, `audit_logging.h`, and `audit-records.h`. Generates `actiontabs.h`, `errtabs.h`, `fieldtabs.h`, `flagtabs.h`, `fstypetabs.h`, `ftypetabs.h`, syscall architecture tables, machine/message/op/perm/io_uring tables using `gen_tables.c` and `gen_tables.h`.

Control flow: `BUILT_SOURCES` drives generated headers before library compilation. Each generator target compiles with `CC_FOR_BUILD` and build flags, includes a specific `_table.h` input through `TABLE_H`, and invokes the generator with options such as `--lowercase`, `--uppercase`, `--duplicate-ints`, `--i2s`, `--s2i`, or `--i2s-transtab`. Architecture table generation is conditional on `USE_ARM`, `USE_AARCH64`, and `USE_RISCV`.

State and persistence: Produces generated header files consumed by `lookup_table.c` and libaudit translation APIs. Installs library, headers, and `audit.pc`.

Dependencies and integration: Depends on configure conditionals, libcap-ng link flags, common library, kernel headers, and generated table inputs. Cross-compilation support depends on `AX_PROG_CC_FOR_BUILD`.

Risks: Generator inputs and flags define public translation behavior, so stale tables or wrong conditional inclusion causes incorrect syscall/name mapping. Cross builds need build-host generator binaries, not target binaries. `VERSION_INFO` controls libtool ABI versioning and must be handled carefully.

Test signals: `make -C lib`, cross-build generation checks, `make distcheck`, translation API unit tests, and diffing generated headers after table updates.
