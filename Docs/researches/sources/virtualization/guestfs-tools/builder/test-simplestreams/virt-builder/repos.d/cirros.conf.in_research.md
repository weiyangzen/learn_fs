# File Research: sources/virtualization/guestfs-tools/builder/test-simplestreams/virt-builder/repos.d/cirros.conf.in

## Scope

Repository configuration template for Simplestreams tests.

## Contents

- Defines `[test-cirros]`.
- Points `uri` to `file://@abs_top_builddir@/builder/test-simplestreams`.
- Sets `format=simplestreams`.

## Risks And Invariants

- Configure substitutes the build directory.
- The format flag is required so virt-builder uses the Simplestreams parser instead of native index parsing.
