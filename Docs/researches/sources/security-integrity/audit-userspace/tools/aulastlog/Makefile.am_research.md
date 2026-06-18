<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/aulastlog/Makefile.am

**Purpose**
This Automake file builds and installs `aulastlog`, a lastlog-like audit-log reporter.

**Important APIs, Types, And Functions**
It sets clean artifacts, distributes `aulastlog.8`, includes project and auparse headers, builds `bin_PROGRAMS = aulastlog`, declares `aulastlog-llist.h` as a non-installed header, and compiles `aulastlog.c` with `aulastlog-llist.c`. The binary links `${top_builddir}/auparse/libauparse.la`.

**Control Flow**
The standard Automake build compiles the list and CLI source files, links auparse, and installs the binary and man page.

**State And Persistence**
No runtime state is represented here. The file controls build artifacts and distribution content.

**Dependencies And Integration Points**
`aulastlog` is integrated with auparse and the audit-userspace tool install path.

**Risks**
There is no listed local test subdirectory for `aulastlog`, so the list implementation and CLI behavior rely on broader build/test coverage or manual testing.

**Test Signals**
A successful build confirms source/link compatibility with auparse; this file does not register runtime tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulastlog/Makefile.am -->
