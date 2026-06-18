<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/ausyscall/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/ausyscall/Makefile.am

**Purpose**
This Automake file builds and installs the `ausyscall` syscall name/number lookup utility.

**Important APIs, Types, And Functions**
It configures project and lib include paths, `_GNU_SOURCE`, `bin_PROGRAMS = ausyscall`, distributes `ausyscall.8`, and compiles `ausyscall.c`. The binary links against `${top_builddir}/lib/libaudit.la`.

**Control Flow**
Automake compiles the single C file and links it with libaudit during the tools build.

**State And Persistence**
The makefile defines build state only. The resulting tool is a pure lookup/reporting command.

**Dependencies And Integration Points**
It integrates with the libaudit syscall translation tables and the audit-userspace installation layout.

**Risks**
Feature-dependent architecture support is controlled by configure macros in the C file; the makefile itself does not express those variants.

**Test Signals**
There is no explicit test target here. Successful compile/link verifies libaudit API compatibility.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/ausyscall/Makefile.am -->
