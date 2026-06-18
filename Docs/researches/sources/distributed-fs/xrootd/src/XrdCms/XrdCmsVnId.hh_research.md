# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsVnId.hh

## Purpose

`XrdCmsVnId.hh` documents and defines the ABI for CMS virtual node-identification plugins loaded through the `all.vnidlib` directive. It supports container/VM deployments where hostnames or IP addresses change and are unsuitable for stable node tracking.

## Important APIs and Types

The macro `XrdCmsgetVnIdArgs` expands to the required `extern "C" std::string XrdCmsgetVnId(...)` signature: an `XrdSysError` reference, configuration file path, plugin parameters, node role character, and maximum allowed return length. The role values are `m`, `s`, and `u` for manager, server, and supervisor, with uppercase variants for proxy roles.

## Control Flow

During initialization, CMS loads the plugin and calls `XrdCmsgetVnId` once. Returning a non-empty string within `mlen` succeeds; returning an empty/null-equivalent string or an overlong ID aborts initialization.

## State and Persistence Behavior

The plugin ABI is called only once and need not be thread-safe. The returned ID becomes part of the virtual-network identity used to track nodes instead of host/IP identity.

## Dependencies and Integration Points

Plugins include this header, `XrdSysError`, and usually `XrdVersion.hh` to declare `XrdVERSIONINFO`. The ABI integrates with CMS node-registration and identity tracking.

## Risks and Edge Cases

The documentation contains typos but the ABI is clear. Plugins must use the exact unmangled C symbol and respect maximum length. Non-deterministic IDs would defeat stable tracking.

## Test Signals

Plugin-loading tests should verify symbol lookup, role propagation, parameter string handling, max-length enforcement, and initialization failure on empty ID.
