# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/security_/CustomizedCallbackHandler.java

## Purpose

`CustomizedCallbackHandler` is an extension point for handling SASL callbacks not recognized by the forked Hadoop RPC SASL server code.

## APIs and control flow

The main method is `handleCallbacks(List<Callback>, String name, char[] password)`. The nested `Cache` resolves a configured class by key, caches it, and falls back to `DefaultHandler` if instantiation fails or the configured class is default. Non-interface objects are adapted reflectively by looking for a `handleCallbacks(List, String, char[])` method. `DefaultHandler` throws `UnsupportedCallbackException` for the first unknown callback.

## State, dependencies, and integration

Global state is a synchronized static map from config key to handler. Dependencies include Hadoop `Configuration`, Java callback APIs, reflection, and SLF4J. `SaslRpcServer.SaslDigestCallbackHandler` uses it for unknown DIGEST callbacks after resolving token username and password.

## Risks and test signals

The cache key is only the config key, not the configured class or configuration instance, so class changes can be hidden until `clear()` is called. Reflection wraps invocation failures as `IOException`. Tests should cover default fallback, custom interface implementation, reflective delegate, instantiation failure, cache clearing, and unknown callback propagation.
