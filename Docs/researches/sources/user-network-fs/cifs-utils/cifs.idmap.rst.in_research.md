<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.idmap.rst.in -->
# sources/user-network-fs/cifs-utils/cifs.idmap.rst.in

## Purpose

`cifs.idmap.rst.in` is the manual-page template for the `cifs.idmap` request-key helper.

## Important APIs, Types, and Functions

The template documents the command synopsis, `--help`, `--timeout`, `--version`, the `cifs.idmap` key type, request-key configuration, plugin path substitution via `@pluginpath@`, and helper path substitution through `@sbindir@`.

## Control Flow

During the build, `Makefile.am` substitutes configured paths and `rst2man` converts the resulting RST into `cifs.idmap.8`. At runtime the documented flow is kernel request-key invoking `cifs.idmap` with a key id, after which the helper maps SID/ID data and instantiates the key.

## State and Persistence Behavior

The document describes key timeout behavior and the operational dependency on the configured plugin symlink. It does not itself persist state.

## Dependencies and Integration Points

It integrates with request-key configuration, `mount.cifs(8)`, the `cifsacl` mount option, and the ID mapping plugin path.

## Risks and Edge Cases

If `@pluginpath@` or `@sbindir@` substitutions are stale, packaged docs will point users to wrong paths. The fallback behavior when helper/plugin is unavailable should remain aligned with kernel and utility behavior.

## Test Signals

Build tests should generate the manpage and inspect substituted paths. Documentation tests should compare option names and defaults with `cifs.idmap.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.idmap.rst.in -->
