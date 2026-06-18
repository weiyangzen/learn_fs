# sources/distributed-fs/tahoe-lafs/src/allmydata/util/attrs_provides.py

## Purpose

This module restores the `attrs` validator pattern for requiring that an attribute value provide a zope interface. It exists because native attrs support for zope interfaces was deprecated while Tahoe-LAFS still uses zope interfaces heavily.

## APIs and control flow

`provides(interface)` returns a `_ProvidesValidator` instance. The validator checks `interface.providedBy(value)` during attrs initialization and raises `TypeError` with the attribute, expected interface, and offending value if the contract is not met. `_ProvidesValidator` is itself an attrs class with slots, hash support, and a concise repr for diagnostics.

## State, dependencies, risks, and tests

State is just the interface object captured by the validator. Dependencies are `attr._make.attrs` and `attrib`, plus zope-interface semantics supplied by the passed interface. Integration appears in modules such as `eliotutil.py`, where optional Eliot logger attributes are validated.

Risks include relying on private attrs internals (`attr._make`) and only checking runtime interface provision, not structural type hints. Test signals should verify success for implementing objects, `TypeError` content for non-providers, repr readability, and compatibility with attrs validators such as `optional(provides(...))`.
