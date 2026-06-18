# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ConfigOptions.java

Purpose: native wrapper for parsing/serializing RocksDB option strings and files. APIs configure delimiter, unknown-option handling, environment, escaped input strings, and sanity-check level.

Control flow loads the RocksDB library before native allocation, then forwards setters to native config options. `setEnv(Env)` passes the environment native handle but does not retain a Java field, so callers must ensure relevant lifetime. `setSanityLevel` maps `SanityLevel` to a byte. State is transient native parser configuration used by APIs such as `DBOptions.getDBOptionsFromProps`.

Risks: no Java-side getters for verification, env lifetime is not retained here, invalid delimiter/escape combinations can alter parsing, and unknown-option tolerance can hide config drift. Tests should parse representative option strings/properties with strict and permissive modes, exercise escaped values, sanity levels, and env-backed parsing.
