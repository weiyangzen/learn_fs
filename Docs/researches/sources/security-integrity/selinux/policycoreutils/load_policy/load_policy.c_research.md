<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/load_policy/load_policy.c -->
# sources/security-integrity/selinux/policycoreutils/load_policy/load_policy.c

## Purpose

Implements the `load_policy` utility that loads the installed SELinux policy, with compatibility warnings for obsolete positional policy/boolean arguments. The source was read completely for this report (89 lines).

## Important APIs, Types, and Functions

`usage()` prints syntax. `main()` handles `-b`, `-q`, and `-i`; quiet mode disables sepol debug; init mode calls `selinux_init_load_policy(&enforce)`, otherwise `selinux_mkload_policy(0)`.

## Control Flow

After optional NLS setup, the utility parses flags, warns about deprecated arguments unless quiet, chooses init-load or normal load, and exits with distinct codes for enforcing init-load failure or general load failure.

## State and Persistence Behavior

No persistent state beyond loading kernel SELinux policy through libselinux. Local state tracks quiet/init/enforce and getopt positions.

## Dependencies and Integration Points

Depends on libselinux policy loading, libsepol debug control, gettext when enabled, and the load_policy Makefile build flags.

## Risks and Edge Cases

Risks are behavior differences during early boot/init mode, maintaining legacy CLI compatibility, and correct exit status for init systems.

## Test Signals

Signals include quiet/deprecated argument behavior, init-load enforcing failure path, normal policy load, and NLS-enabled builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/load_policy/load_policy.c -->
