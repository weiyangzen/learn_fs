# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_consumer.py

## Purpose
This file tests `MemoryConsumer`, a utility consumer that accumulates bytes written by Twisted producers. It covers both push and pull producer modes.

## Important APIs, Types, And Functions
The local `Producer` implements both `IPushProducer` and `IPullProducer` and drives test data into a `MemoryConsumer`. `MemoryConsumerTests` has `test_push_producer` and `test_pull_producer`.

## Control Flow
For push mode, registering the producer with `streaming=True` triggers `resumeProducing`, which writes the first chunk. The test manually calls `iterate` for remaining chunks and once more to finish, expecting `consumer.done` only after unregistering. For pull mode, registering with `streaming=False` causes the consumer to pull all chunks immediately.

## State, Persistence, And Dependencies
State is in `Producer.data`, `Producer.done`, and `MemoryConsumer.chunks/done`. There is no persistence. The tests depend on Twisted producer interfaces.

## Risks And Test Signals
The file catches producer registration regressions, premature completion, and chunk accumulation failures. Broader helper behavior such as `download_to_data` is intentionally covered elsewhere by filenode tests.
