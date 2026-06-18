<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucXAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucXAttr.hh

## Purpose

`XrdOucXAttr.hh` defines a template wrapper around XRootD filesystem extended attributes. It lets callers bind a typed attribute payload object to `Del`, `Get`, and `Set` operations without repeating xattr name, size, and pre/post formatting code.

## Important APIs, Types, And Functions

- The template parameter `T` must provide `Name()`, `sizeGet()`, `sizeSet()`, `postGet(int)`, and `preSet(T&)`.
- `XrdOucXAttr<T>::Attr` is the in-object typed attribute value.
- `Del(const char *Path, int fd = -1)` calls `XrdSysFAttr::Xat->Del()`.
- `Get(const char *Path, int fd = -1)` reads into `Attr` and lets `postGet()` transform or validate the result.
- `Set(const char *Path, int fd = -1)` lets `preSet()` return either `this` or a formatted temporary object before writing.

## Control Flow

The wrapper is thin: callers populate or inspect `Attr`; operations delegate to the active `XrdSysFAttr` implementation with either a path or a file descriptor. `Set()` creates a stack temporary `T xA`, passes it to `Attr.preSet(xA)`, then writes from the returned pointer for `Attr.sizeSet()` bytes.

## State And Persistence

The only instance state is `Attr`. Persistence is external: the actual xattr value is stored on the target filesystem object through the active xattr backend.

## Dependencies And Integration Points

The template depends on `XrdSys/XrdSysFAttr.hh` and the global `XrdSysFAttr::Xat` backend. It is a reusable adapter for code that stores metadata in filesystem xattrs, including cache metadata paths elsewhere in XRootD.

## Risks And Edge Cases

- `XrdSysFAttr::Xat` is dereferenced without a null check.
- Template requirements are documented by comments, not enforced by concepts or traits.
- `preSet()` can return a pointer to invalid storage if implemented incorrectly.
- The API assumes `sizeGet()` and `sizeSet()` match the serialized format of `T`.

## Test Signals

Tests should use a fake `XrdSysFAttr` backend and a sample `T` to verify path and fd forms, `postGet()` return propagation, `preSet()` temporary formatting, delete errors, and behavior when payload sizes differ from object size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucXAttr.hh -->
