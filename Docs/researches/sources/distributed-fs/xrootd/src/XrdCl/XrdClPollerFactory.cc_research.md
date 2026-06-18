# sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerFactory.cc

## Purpose

This file implements `PollerFactory::CreatePoller`, which chooses a concrete socket event poller from a comma-separated preference list. In this source snapshot the only registered backend is `"built-in"`.

## Important APIs, Types, And Functions

The anonymous `createBuiltIn()` returns `new PollerBuiltIn()`. `CreatePoller(preference)` builds a local map from poller names to creator functions, logs available pollers, splits the preference string with `Utils::splitString`, and returns the first matching implementation.

## Control Flow

If `preference` is empty, the function logs an error and returns null. Otherwise it iterates preference tokens in order. Unknown tokens are logged at debug level and skipped. The first known token creates and returns a poller immediately. If no token matches, the function returns null.

## State And Persistence Behavior

There is no persistent state and no static registry beyond the function-local map rebuilt on each call. The caller owns the returned `Poller*`.

## Dependencies And Integration Points

The factory includes `PollerFactory.hh`, `PollerBuiltIn.hh`, `Constants`, `Log`, `Utils`, and `DefaultEnv`. `PostMaster::Initialize` calls it using the environment's `PollerPreference` value.

## Risks And Edge Cases

Preference tokens are not trimmed here; split behavior determines whether `"built-in, other"` matches the second token. The registry is not externally extensible without source changes. A null return prevents `PostMaster` initialization.

## Test Signals

Tests should cover empty preference, known first token, unknown tokens before known token, all-unknown preferences, and logging/ownership expectations for the created poller.
