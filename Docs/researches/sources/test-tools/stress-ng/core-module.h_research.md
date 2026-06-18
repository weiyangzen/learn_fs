# sources/test-tools/stress-ng/core-module.h

Purpose: declares the module load/unload interface for stressors.

Important APIs/types: `stress_module_load(name, alias, options, already_loaded)` and `stress_module_unload(name, alias, already_loaded)`.

Control flow: none in the header; signatures document that load reports whether the module was already present and unload can skip preexisting modules.

State/persistence: no local state, but declared APIs can change kernel module state.

Dependencies/integration: included by module stressor code and implemented by `core-module.c`.

Risks: callers must preserve `already_loaded` from load to unload or they may remove modules that predated the test.

Test signals: compile users across libkmod/stub builds and verify callers handle negative returns.
