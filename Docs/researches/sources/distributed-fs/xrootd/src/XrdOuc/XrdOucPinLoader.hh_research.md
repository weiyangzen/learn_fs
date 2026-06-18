<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.hh

Purpose: Declares the standard versioned plugin loader used throughout XRootD utility and server code.

APIs and control flow: Constructors support diagnostics through an error router, caller buffer, or internal buffer. `Resolve()` loads and resolves symbols, `Global()` controls exported symbol visibility, `Export()` transfers the plugin object, `Path()` exposes the selected path, `LastMsg()` returns buffered diagnostics, and `Unload()` drops the image management object.

State and persistence: The loader owns path strings, diagnostics storage, and optionally an `XrdSysPlugin`. Deleting a loader normally persists a loaded plugin image.

Dependencies and integration: Forward-declares `XrdSysError`, `XrdSysPlugin`, and `XrdVersionInfo` to keep the public loader header light.

Risks and test signals: Callers must understand that `Export()` disables destructor management and that `Unload(true)` deletes the loader itself. Tests should check ownership transfer, optional symbol prefixes, error-buffer truncation, and compatibility with third-party plugin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.hh -->
