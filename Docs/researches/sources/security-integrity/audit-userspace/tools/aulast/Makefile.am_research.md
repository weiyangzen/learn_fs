<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/aulast/Makefile.am

**Purpose**
This Automake file builds and installs the `aulast` command, which reports login/logout sessions from audit logs.

**Important APIs, Types, And Functions**
It declares `SUBDIRS = test`, installs `bin_PROGRAMS = aulast`, ships `aulast.8`, and treats `aulast-llist.h` as a non-installed header. `aulast_SOURCES` are `aulast.c` and `aulast-llist.c`. The binary links against `${top_builddir}/auparse/libauparse.la`.

**Control Flow**
The recursive build enters the `test` subdirectory, compiles the two source files with `_GNU_SOURCE` and project include paths, links against auparse, and includes the man page in distribution.

**State And Persistence**
No runtime state is defined here. Build state includes object files, generated artifacts, and clean-file patterns.

**Dependencies And Integration Points**
The tool integrates with the auparse library and the audit-userspace install layout. The test subdirectory provides linked-list tests for the internal list implementation.

**Risks**
The `aulast` binary depends on internal list code rather than a shared utility library. Changes to auparse APIs or include paths can break the tool build.

**Test Signals**
The adjacent test makefile builds `aulast_llist_test`, giving coverage for the list library that `aulast.c` relies on.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/Makefile.am -->
