# File Research: sources/virtualization/nvme-cli/libnvme/meson.build

This is the libnvme root Meson entry for building the bundled library or finding an installed one.

Core behavior when `want_libnvme`:
- Optionally checks OpenSSL HKDF behavior by running `test/hkdf_add1.c`.
- Generates `libnvme.spec` from the template.
- Enters generator, `src`, Python bindings, tests, examples, and docs subdirectories based on options.

Fallback behavior:
- If not building bundled libnvme, finds installed libnvme through pkg-config for standard prefixes or compiler library lookup for non-standard prefixes.

Integration role:
- Top-level build orchestrator for libnvme inside nvme-cli.
