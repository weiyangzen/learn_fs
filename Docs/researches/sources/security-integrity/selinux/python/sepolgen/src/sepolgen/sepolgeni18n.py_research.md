# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/sepolgeni18n.py

## Purpose
This tiny module provides the `_()` translation function used by sepolgen callers. It centralizes gettext setup for the `selinux-python` message catalog.

## Important APIs, Types, And Functions
The only exported behavior is `_`. On success, `_` is bound to `gettext.translation("selinux-python", localedir="/usr/share/locale", fallback=True).gettext`. On any import/setup failure, `_` falls back to an identity function returning the original string.

## Control Flow
Import-time code tries to import `gettext`, construct a translation object with fallback enabled, and bind `_`. The fallback `except` handles all errors and defines a local identity function.

## State And Persistence Behavior
State is import-time only. No files are written. Runtime translation depends on system locale and installed `.mo` files under `/usr/share/locale`, but `fallback=True` avoids hard failure when catalogs are absent.

## Dependencies And Integration Points
It depends only on Python `gettext` and the system locale catalog path. Other sepolgen modules can import `_` for translatable messages without carrying gettext setup.

## Risks And Edge Cases
The broad bare `except` hides all setup problems, including coding errors. The fallback function shadows built-in-style `_` naming and uses parameter name `str`, which shadows the type but is harmless here. The localedir is hard-coded, so relocatable installs may silently run untranslated.

## Test Signals
Tests should cover import with gettext available, missing catalog fallback, forced gettext import/setup failure, and identity behavior for untranslated strings.
