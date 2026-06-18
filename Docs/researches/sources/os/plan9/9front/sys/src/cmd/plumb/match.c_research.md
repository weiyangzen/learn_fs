# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/match.c

`match.c` evaluates plumber rules against `Plumbmsg` objects. It implements verbs such as `is`, `matches`, `isfile`, `isdir`, `set`, `add`, and `delete`, including full-string regex matching, click-position-aware regex matching, attribute mutation, destination/data/type/wdir/src rewriting, and filesystem checks relative to message working directory.

`Exec` state stores regex captures, derived `$file`/`$dir`, click rewrite flags, and pending client behavior. After all pattern rules match, `matchruleset()` may set a default destination from the ruleset port and rewrite clicked data to `$0`.

Startup actions build an argv vector with variable expansion and spawn a client process. `client` actions can hold the message until the client opens its port.
