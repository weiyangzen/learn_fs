# sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/SameKeyReader.java

## Purpose
`SameKeyReader` is a Freon command that repeatedly reads the same Ozone key from multiple threads. It is intended to test read-side OM/client performance and caching behavior for a single hot key.

## Important APIs, Types, and Functions
The command extends `OzoneClientKeyValidator` and implements `Callable<Void>`. It registers as `ocokr`/`ozone-client-one-key-reader`. The required `--key`/`-k` option supplies the key name. The only override, `generateObjectName(long counter)`, ignores the counter and always returns that configured key name.

## Control Flow
All execution mechanics come from `OzoneClientKeyValidator`; this class customizes the object-name generator so each iteration targets the same key rather than a per-counter name.

## State and Persistence Behavior
The class has one mutable field, `keyName`, populated by picocli. It does not create or mutate persistent data; it reads an existing key through inherited validator logic.

## Dependencies and Integration Points
It integrates with Freon's Ozone client key validation framework, including inherited configuration for volume, bucket, thread count, object size, and metrics.

## Risks and Edge Cases
The command requires the key to exist in the inherited target volume/bucket. Because every thread reads the same object, results are intentionally skewed toward hot-object behavior and are not representative of random-read workloads.

## Test Signals
There is no direct test in this subset. Coverage would come from inherited `OzoneClientKeyValidator` tests or integration tests against a prepared bucket/key.
