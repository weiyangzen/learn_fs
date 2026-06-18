# sources/distributed-fs/tahoe-lafs/src/allmydata/util/eliotutil.py

## Purpose

This module bridges Tahoe-LAFS with Eliot structured logging. It supplies validators, CLI option handlers for destinations, a Twisted service that installs Eliot destinations, relays Twisted and stdlib logging into Eliot, and a decorator for Deferred-returning logged calls.

## APIs and control flow

`validateInstanceOf()` and `validateSetMembership()` create Eliot validators. `eliot_logging_service()` parses destination factories and returns `_EliotLogging`, a `MultiService` that wraps destinations in `ThreadedWriter`, installs stdlib and Twisted observers on start, and removes them on stop. `opt_eliot_destination()` parses `file:<path>` destination strings and appends factories to Twisted Options; `opt_help_eliot_destinations()` prints help.

`_TwistedLoggerToEliotObserver` flattens Twisted events with `eventAsJSON`, removes nonserializable fields, and writes Eliot messages. `_StdlibLoggingToEliotHandler` writes stdlib records and tracebacks. `_DestinationParser` supports stdout via `-` or rotating `LogFile`s. `log_call_deferred()` wraps a Deferred-returning function in an Eliot action and finishes when the Deferred fires.

## State, dependencies, risks, and tests

State is installed observers, logging handlers, and destination writer services. Dependencies include Eliot, Twisted logging/service/options, attrs validators, `jsonbytes.AnyBytesJSONEncoder`, and local `provides`.

Risks include duplicate observer installation, JSON serialization changes in Twisted events, file destination parsing with reserved characters, background writer lifecycle leaks, and logging recursion. Test signals should cover destination parsing, rotate args, stdout destination, service start/stop cleanup, Twisted/stdlib relay output, bytes JSON encoding, UsageError mapping, and Deferred action completion.
