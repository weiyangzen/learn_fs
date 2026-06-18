<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/Makefile.am

**Purpose**
This top-level Automake file declares the audit-userspace command-line tool subdirectories that are part of the tools build.

**Important APIs, Types, And Functions**
It sets `CONFIG_CLEAN_FILES` for generated or rejected build artifacts and declares `SUBDIRS = aulast aulastlog ausyscall`.

**Control Flow**
Automake recurses into the three subdirectories during build, install, clean, and test phases according to the parent target.

**State And Persistence**
The file has no runtime state. It affects build output and cleanup behavior only.

**Dependencies And Integration Points**
It is integrated into the project’s recursive Automake build. The child directories define the actual programs, man pages, and tests.

**Risks**
Adding a new tool without listing it here means it will not be built through the standard recursive path. Conversely, broken child makefiles stop parent tool builds.

**Test Signals**
There is no direct test logic, but successful recursive `make`/`make check` through this directory confirms the declared tool subtrees are buildable.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/Makefile.am -->
