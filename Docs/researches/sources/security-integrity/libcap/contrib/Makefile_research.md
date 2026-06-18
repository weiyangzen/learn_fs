<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/Makefile -->
# sources/security-integrity/libcap/contrib/Makefile

## Purpose
Contrib makefile that dispatches build and clean targets into bug demonstration subdirectories.

## Important APIs, Types, And Functions
Defines phony `all` and `clean` targets that loop over `bug*` directories.

## Control Flow
For each matching directory, invokes `$(MAKE) -C $$x $@` and exits on the first failure.

## State And Persistence Behavior
Delegates all artifact creation/removal to child makefiles.

## Dependencies And Integration Points
Integrates the contrib bug reproducer directories into a simple aggregate target.

## Risks And Edge Cases
Only directories matching `bug*` are included; other contrib tools such as `capso` or scripts are not dispatched.

## Test Signals
Signals are successful recursive make completion for all bug directories.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/Makefile -->
