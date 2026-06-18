# sources/test-tools/stress-ng/core-madvise.h

## Purpose

This header exposes stress-ng's memory-advice option arrays and helper APIs.

## Important APIs, Types, And Functions

It declares `madvise_options`, `madvise_options_elements`, advice sanitization, random advice, common advice wrappers, and process-wide page advice.

## Control Flow

Callers can enumerate available advice values or apply named helpers without duplicating platform preprocessor checks.

## State And Persistence Behavior

The implementation mutates VM advice on mappings but owns no persistent state.

## Dependencies And Integration Points

The API integrates with mmap/memory stressors and option flags controlling madvise behavior.

## Risks And Test Signals

Callers must understand which advice may alter data or mapping behavior. Tests should cover array availability only when `HAVE_MADVISE` is defined and wrapper no-op behavior otherwise.
