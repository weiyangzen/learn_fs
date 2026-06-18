# File Research: sources/virtualization/nbdkit/plugins/example4/Makefile.am

Build/install definition for the Perl example plugin.

Key contents:
- Uses `example4.pl` as source.
- Installs generated script `nbdkit-example4-plugin` when Perl support is available.
- Rewrites `@sbindir@` in the shebang to the configured `sbindir`.
- Marks generated script executable.
- Generates POD documentation when available.
