<!-- BEGIN_FILE_RESEARCH: sources/test-tools/crashmonkey/Makefile -->
# sources/test-tools/crashmonkey/Makefile

Purpose: builds CrashMonkey from local C++ sources, selecting compiler/linker flags, object layout, and clean targets for the crash-consistency test tool.

Important APIs/types/functions: make variables `CODEDIR=code`, `SUBDIRS=$(CODEDIR)`, `SUBDIRS_CLEAN=$(addsuffix .clean, $(SUBDIRS))`, `BUILD_DIR=build`; targets `.PHONY`, `all`, `tests`, `seq1`, `gentests`, `permuters`, `clean`; command surface `make`, `rm` through recipes.

Control flow: The default target compiles CrashMonkey C++ objects and links the final binary; `clean` removes generated objects and executables. Build behavior is driven by make dependencies rather than a shell test entry point.

State and persistence behavior: touches state paths such as `$(CODEDIR)`, `$(addsuffix .clean, $(SUBDIRS)`, `$(SUBDIRS)`, `$(SUBDIRS_CLEAN)`, `$(MAKE)`, `$(subst .clean, , $@)`.

Dependencies and integration points: integrates with the blktests `crashmonkey` suite and the shared harness.

Risks and test signals: primary risk is build or harness drift; signal is make/shell exit status.
<!-- END_FILE_RESEARCH: sources/test-tools/crashmonkey/Makefile -->
