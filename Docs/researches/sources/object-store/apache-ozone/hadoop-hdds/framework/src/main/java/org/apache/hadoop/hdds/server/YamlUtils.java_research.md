# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/YamlUtils.java

## Purpose

`YamlUtils` centralizes safe-ish YAML loading and atomic YAML dumping for HDDS/Ozone server code.

## Important APIs, Types, and Functions

Static `LOADER` is created by `getYamlForLoad`, which configures SnakeYAML `LoaderOptions` with a `TagInspector` that allows tags whose class names start with `org.apache.hadoop.hdds.` or `org.apache.hadoop.ozone.`. `loadAs(InputStream, Class<? super T>)` delegates to the shared loader. `dump(Yaml, Object, File, Logger)` writes UTF-8 YAML through `AtomicFileOutputStream` and logs/rethrows IO failures.

## Control Flow

Load callers use the preconfigured loader. Dump callers pass their chosen `Yaml` instance and data; the method writes atomically and closes streams with try-with-resources.

## State and Persistence Behavior

The shared loader is static. Dumping persists YAML to a target file atomically to avoid partial writes.

## Dependencies and Integration Points

It integrates SnakeYAML, Ratis atomic file output streams, UTF-8 encoding, and server loggers. It is used by code that reads/writes Ozone YAML state or configuration-like files.

## Risks and Edge Cases

Allowed tag prefixes are broad within Ozone/HDDS packages; unsafe classes under those packages would be loadable. `loadAs` does not close the input stream. Dump safety depends on caller-provided `Yaml` configuration.

## Test Signals

Test allowed and rejected YAML tags, typed load behavior, atomic dump content, exception logging/rethrow on IO failure, and UTF-8 output.
