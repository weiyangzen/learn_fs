# sources/distributed-fs/xrootd/python/src/PyXRootDModule.cc

## Purpose
This source defines the `client` Python extension module for PyXRootD and registers all exposed types and module-level helper functions.

## Important APIs, Types, and Functions
It declares global `ClientModule`, `module_methods`, `moduledef`, and `PyInit_client`. Registered functions include finalization, environment getters/setters, version/log controls, and `setXAttrAdler32_cpp`. Registered types are `FileSystem`, `File`, `URL`, and `CopyProcess`.

## Control Flow
`PyInit_client` readies each type by setting `tp_new`, calling `PyType_Ready`, and increfing the type. It creates the module and adds type objects with `PyModule_AddObject`, then returns the module.

## State and Persistence
Module state size is `-1`, meaning global state rather than per-interpreter module state. It stores the module pointer globally. No persistence beyond process/module lifetime.

## Dependencies and Integration Points
Includes all binding headers, environment/finalization helpers, and Adler-32 helper. It is the entry point compiled by the Python extension target.

## Risks and Test Signals
`PyModule_AddObject` steals references; the prior increfs align with that, but failure paths after partial module creation are not extensively cleaned up. `m_size = -1` is not subinterpreter-friendly. Test signals are successful import, attribute presence, repeated import, type construction, and module finalization behavior.
