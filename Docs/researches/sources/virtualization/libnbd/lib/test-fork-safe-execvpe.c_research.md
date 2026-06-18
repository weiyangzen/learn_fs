# File Research: sources/virtualization/libnbd/lib/test-fork-safe-execvpe.c

Helper binary for testing `nbd_internal_execvpe_init` and `nbd_internal_fork_safe_execvpe`.

Flow:
- Expects `program-to-exec argv0 ...`.
- Builds a null-terminated `string_vector` for target argv.
- Initializes execvpe context for the program.
- Prints generated candidate pathnames to stdout.
- Calls fork-safe execvpe directly; on failure prints machine-readable errno names for selected errors.

Interactions:
- Tests utility functions from `utils.c`.
- Uses process `environ`.
- Paired with `test-fork-safe-execvpe.sh`.

Research notes:
- The helper does not fork itself; it exercises the child-side exec function in a controlled standalone process.
