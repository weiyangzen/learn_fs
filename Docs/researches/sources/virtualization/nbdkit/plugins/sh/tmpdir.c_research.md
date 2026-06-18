# File Research: sources/virtualization/nbdkit/plugins/sh/tmpdir.c

Manages the temporary directory and environment for shell scripts. `tmpdir_load` creates a private temporary directory, logs it, and builds a private copy of `environ` with `tmpdir=<path>` added.

`tmpdir_unload` removes the temporary directory with `rm -rf`, ignores cleanup errors, frees the directory path, and frees the copied environment. The command is built from a directory name created by nbdkit utilities, limiting shell-quoting exposure.
