<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/hll/pp/pp.c -->
# sources/security-integrity/selinux/policycoreutils/hll/pp/pp.c

## Purpose

Command-line converter from SELinux binary policy package `.pp` input to CIL output for policycoreutils high-level-language support. The source was read completely for this report (168 lines).

## Important APIs, Types, and Functions

Defines `log_err()`, `usage()`, and `main()`. `main()` parses `-h`, supports stdin/stdout via missing or `-` paths, reads a module package with `sepol_ppfile_to_module_package()`, optionally warns when the output basename does not match the module name, and writes CIL with `sepol_module_package_to_cil()`.

## Control Flow

Control flow is CLI parse, open input/output streams, decode `.pp`, close input, inspect module/output names for warning, convert package to CIL, and clean up streams/package on exit.

## State and Persistence Behavior

State is transient: `struct sepol_module_package *`, FILE handles, duplicated output path for basename manipulation, and static `progname`.

## Dependencies and Integration Points

Depends on libsepol module/package and module-to-CIL APIs, libc getopt/basename/signal handling, and the hll/pp Makefile that links `-lsepol`.

## Risks and Edge Cases

Risks include stream ownership on stdin/stdout, SIGPIPE behavior when consumers close output, basename mutation of duplicated paths, and user confusion from module-name/output-name mismatch.

## Test Signals

Signals include converting known `.pp` packages, stdin/stdout mode, invalid package failures, broken pipe handling, and warning coverage for mismatched names.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/hll/pp/pp.c -->
