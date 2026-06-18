# sources/user-network-fs/impacket/tests/dot11/__init__.py

## Purpose
This package initializer marks `impacket/tests/dot11` as a Python test package. It contains only the shebang, copyright/license header, and no executable imports or package-level fixtures.

## Important APIs, Types, and Functions
There are no classes, functions, variables, or exported test helpers. Its only functional role is package discovery/compatibility for the sibling dot11 unittest modules.

## Control Flow
No runtime control flow exists. Importing the package executes no side effects beyond loading the empty module.

## State and Persistence Behavior
No state is created, mutated, cached, or persisted.

## Dependencies and Integration Points
It integrates indirectly with Python's import system and test discovery. Sibling files import from `impacket.dot11` and `impacket.ImpactDecoder`, but this initializer does not wire those imports.

## Risks
Risk is minimal. Future maintainers should avoid adding side effects here because it would affect all dot11 test imports.

## Test Signals
There are no direct test signals. A successful import of sibling tests implicitly validates that the package initializer does not interfere with discovery.
