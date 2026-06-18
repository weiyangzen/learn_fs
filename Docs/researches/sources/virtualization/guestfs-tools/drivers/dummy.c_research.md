# File Research: sources/virtualization/guestfs-tools/drivers/dummy.c

## Scope

Dummy C source for the OCaml-based `virt-drivers` binary.

## Behavior

- Defines a trivial enum constant so Automake has a valid C source.

## Risks And Invariants

- Build-system shim only; no runtime behavior.
