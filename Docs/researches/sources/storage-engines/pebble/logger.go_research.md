# sources/storage-engines/pebble/logger.go

Purpose: this small public veneer re-exports logging interfaces and defaults from `internal/base` into the Pebble package API.

Important APIs/types/functions: `Logger` aliases `base.Logger`, `DefaultLogger` aliases `base.DefaultLogger`, and `LoggerAndTracer` aliases `base.LoggerAndTracer`.

Control flow: there is no executable control flow beyond package initialization of the exported variable alias. Consumers configure `Options.Logger` or related tracing/logging paths using these exported names while implementation code continues to depend on the base package definitions.

State and persistence behavior: no mutable state is introduced here. `DefaultLogger` points to the base default, which logs through the Go standard library logging implementation.

Dependencies and integration points: this file is part of Pebble's external API compatibility surface. It prevents users from importing internal packages to name logger types. Internal components such as iterators, DB checks, and options use the logger interface for fatal diagnostics and normal logging.

Risks and test signals: risk is primarily API compatibility. Changing these aliases would break downstream code or documentation. There are no dedicated tests in this file; coverage comes from compilation and any tests that instantiate `Options` with custom loggers.
