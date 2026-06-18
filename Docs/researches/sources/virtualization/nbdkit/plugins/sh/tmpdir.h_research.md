# File Research: sources/virtualization/nbdkit/plugins/sh/tmpdir.h

Header for shell-plugin temporary environment support. It declares global `tmpdir`, copied `env`, and the `tmpdir_load`/`tmpdir_unload` lifecycle functions.

This state is consumed by the process runner so child scripts receive the private temp directory in their environment.
