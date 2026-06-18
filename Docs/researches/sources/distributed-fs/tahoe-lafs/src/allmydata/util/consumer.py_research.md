# sources/distributed-fs/tahoe-lafs/src/allmydata/util/consumer.py

## Purpose

This module provides a simple Twisted `IConsumer` that accumulates downloaded bytes in memory. It is used by filenode read paths when a caller wants the whole requested range as one bytes object.

## APIs and control flow

`MemoryConsumer` stores `chunks`, `done`, and the producer. `registerProducer()` starts a streaming producer once or repeatedly calls `resumeProducing()` for non-streaming producers until `unregisterProducer()` marks completion. `write()` appends bytes. `download_to_data(n, offset=0, size=None)` calls `n.read(MemoryConsumer(), offset, size)` and joins collected chunks in a callback.

## State, dependencies, risks, and tests

State is in-memory downloaded data; there is no disk persistence. Dependencies are zope interface implementation and Twisted `IConsumer`. Integration is direct with filenode `read()` implementations and producer/consumer flow control.

Risks include unbounded memory use for large downloads, synchronous loops for non-streaming producers that depend on correct producer behavior, and lack of pause/resume/backpressure beyond the basic interface. Test signals should exercise streaming and non-streaming producers, offset/size reads through a fake filenode, chunk ordering, empty downloads, and Deferred error propagation.
