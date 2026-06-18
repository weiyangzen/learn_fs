# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/io/LengthOutputStream.java

## Purpose
Counts bytes written while forwarding all writes to an underlying `OutputStream`.

## Important APIs, Types, And Functions
Extends `FilterOutputStream`. Public method `getLength()` returns an `int` counter. Overrides `write(int)` and `write(byte[], int, int)`.

## Control Flow
Each write delegates to `out` first, then increments length by one or by `len`. Exceptions from the underlying stream prevent counter increments.

## State And Persistence
State is an in-memory `int length`; output persistence is owned by the wrapped stream.

## Dependencies And Integration Points
Can be used when serialization code needs to measure emitted byte length without buffering all output.

## Risks
The counter can overflow beyond `Integer.MAX_VALUE`. It does not override `write(byte[])`, but `FilterOutputStream` routes that to the three-argument method. Not synchronized.

## Test Signals
Tests should cover all write overloads, exception-before-count behavior, flush/close forwarding, and large-count overflow expectations.
