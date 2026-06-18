# sources/distributed-fs/xrootd/python/src/PyXRootDCopyProgressHandler.hh

## Purpose
This header declares the C++ progress-handler adapter used by copy operations.

## Important APIs, Types, and Functions
`CopyProgressHandler` subclasses `XrdCl::CopyProgressHandler` and declares overrides for `BeginJob`, `EndJob`, `JobProgress`, and `ShouldCancel`. It stores `PyObject *handler`.

## Control Flow
The header only defines construction and method declarations; implementation lives in the `.cc` file. XrdCl invokes the virtual methods during copy execution.

## State and Persistence
State is the Python handler pointer. No persistence.

## Dependencies and Integration Points
Depends on Python C API, `XrdClCopyProcess`, `XrdClPropertyList`, and `XrdClURL`. Instantiated by `CopyProcess::Run`.

## Risks and Test Signals
No ownership policy is documented in the type itself. Build tests catch virtual signature mismatches; runtime tests should verify Python handler lifetime and callback method names.
