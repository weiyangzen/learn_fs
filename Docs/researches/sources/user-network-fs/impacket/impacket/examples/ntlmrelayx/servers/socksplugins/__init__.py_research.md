# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/__init__.py

## Purpose
`socksplugins/__init__.py` dynamically discovers and registers SOCKS relay plugins for ntlmrelayx. It imports each plugin module in the package and collects its declared plugin class in `SOCKS_RELAYS`.

## Important APIs, Types, and Functions
The only public object is `SOCKS_RELAYS`, a set of plugin classes. Import-time code uses `importlib.resources.files()` to enumerate package files, imports each non-dunder `.py` module, reads its `PLUGIN_CLASS` global, resolves that class from the module, and adds it to the set.

## Control Flow
On package import, the directory `impacket.examples.ntlmrelayx.servers.socksplugins` is scanned. Files containing `__` or not ending in `.py` are skipped. The package name is taken from `__spec__.name` with a Python 2 fallback to `__package__`, then modules are imported one by one.

## State and Persistence Behavior
State is limited to the in-memory `SOCKS_RELAYS` set and normal `sys.modules` imports. No files are written.

## Dependencies and Integration Points
It depends on `importlib.resources`, `os`, and `sys`. The SOCKS server uses `SOCKS_RELAYS` to know which protocol plugins are supported.

## Risks and Edge Cases
Discovery is eager: importing one broken plugin can fail the whole package. Plugins must define `PLUGIN_CLASS` and the named class. Set ordering is nondeterministic, so consumers should not depend on registration order.

## Test Signals
Test package import, plugin addition/removal, modules without `PLUGIN_CLASS`, Python packaging from filesystem and zip/importlib resources, and duplicate class handling.
