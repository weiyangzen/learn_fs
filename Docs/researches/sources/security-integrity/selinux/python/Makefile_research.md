<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/Makefile -->
# sources/security-integrity/selinux/python/Makefile

## Purpose
Top-level recursive Makefile for SELinux Python tooling.

## Important APIs, Types, And Functions
Defines `SUBDIRS = sepolicy audit2allow semanage sepolgen chcat po` and forwards `all install relabel clean format test` to each subdirectory.

## Control Flow
For any supported target, it loops through `SUBDIRS`, changes into each directory, invokes `$(MAKE) $@`, and stops on the first failure.

## State And Persistence
State is produced by subdirectory builds and installs; this file itself creates no artifacts.

## Dependencies And Integration Points
It integrates the Python components into the broader SELinux build. Subdirectories contain scripts, libraries, translations, tests, and man pages.

## Risks And Edge Cases
Ordering matters: tools such as `audit2allow` depend on sepolgen modules being installed or importable at runtime, though make recursion does not express fine-grained dependencies. A missing target in any subdir fails the whole target.

## Test Signals
Run each forwarded target in a staged environment and confirm failures propagate. `make test` is the broadest signal because it invokes all subproject tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/Makefile -->
