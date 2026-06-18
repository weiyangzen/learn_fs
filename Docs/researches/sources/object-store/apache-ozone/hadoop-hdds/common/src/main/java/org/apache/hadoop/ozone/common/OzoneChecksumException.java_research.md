# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/OzoneChecksumException.java

## Purpose

`OzoneChecksumException` is a private/evolving `IOException` subtype used to report checksum validation failures in Ozone data paths.

## APIs and control flow

The class provides a message-only constructor and a message-plus-cause constructor. There is no special control flow or extra fields; the type itself is the meaningful signal.

## State, dependencies, and integration

It depends only on Java `IOException` and HDDS audience/stability annotations. It integrates with checksum computation and chunk/block read validation code so callers can distinguish data-integrity failures from generic IO failures.

## Risks and test signals

The class carries no structured checksum details, so diagnostics depend on caller-provided messages. Tests should assert that checksum mismatches throw this specific type and preserve causal exceptions when lower-level checksum code fails.
