# sources/sync-backup/borg/src/borg/_item.c

## Purpose
This C helper provides low-level pointer wrapping/unwrapping for Python objects. It converts a `PyObject *` pointer address into a small `bytes` object and later turns that byte representation back into the original object pointer without serializing or copying the object.

## Important APIs, Types, and Functions
- Includes `Python.h` and uses the CPython C API.
- `_object_to_optr(PyObject *obj)` increments the object's refcount and returns a bytes object containing the address of the local pointer variable's value, sized as `sizeof(void*)`.
- `_optr_to_object(PyObject *bytes)` validates that the input is bytes of pointer-size length, then reads the `PyObject *` value from the bytes payload and returns it.

## Control Flow
Wrapping calls `Py_INCREF(obj)` to keep the object alive, then creates a `PyBytes` payload from the pointer value. Unwrapping validates type and size, raises `TypeError` on invalid inputs, extracts the pointer value with `PyBytes_AsString`, and returns the object pointer. The comments describe the contract that wrap/unwrap calls must be symmetric because the reference increment is conceptually transferred and not decref'd in the unwrap helper.

## State and Persistence Behavior
There is no external persistence, but reference counts are persistent process state. Incorrect pairing of wrap and unwrap can leak references; unwrapping invalid or stale byte payloads can return arbitrary pointers and crash or corrupt process state. The representation is intentionally process-local and cannot survive serialization across processes or interpreter lifetimes.

## Dependencies and Integration Points
This file depends on CPython internals and is likely included or used by the Borg item Cython extension built from `src/borg/item.pyx`/`setup.py`. It integrates with Python object identity/pointer passing where Cython or C code needs to pass object references without msgpack serialization.

## Risks and Edge Cases
- Pointer bytes are not safe across processes, Python interpreters, architectures, or after object lifetime violations.
- The API accepts any bytes object of pointer size, so callers must ensure the payload came from `_object_to_optr`.
- Reference lifecycle correctness relies on strict symmetry; missing unwraps leak references, and duplicate unwrap semantics could be unsafe depending on the surrounding generated code.
- This is CPython-specific and not portable to Python implementations with different object models.

## Test Signals
Tests should cover wrapping/unwrapping live Python objects, invalid type input, invalid byte length input, and reference count behavior under debug builds or leak checks. Fuzzing should avoid arbitrary pointer dereference; validation should focus on caller constraints and generated Cython integration.
