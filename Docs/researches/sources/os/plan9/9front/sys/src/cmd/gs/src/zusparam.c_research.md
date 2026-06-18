# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zusparam.c

## Purpose
Implements user and system parameter operators for Ghostscript.

## Key Elements
Defines `.setsystemparams`, `.currentsystemparams`, `.getsystemparam`, `.setuserparams`, `.currentuserparams`, `.getuserparam`, and Level 2 `.checkpassword`. Parameter definitions cover build/revision data, font cache limits, global/local VM limits, VM reclaim/threshold, stack limits, halftone/font flags, byte order, real format, and file-permission locking.

## Behavior/Risks
System parameter changes require the system-parameters password and may update stored start-job/system passwords. User parameter changes update cached scanner options through `ztoken_scanner_options`. Parameter setting is not transactional; the file explicitly notes it does not roll back earlier successful changes if a later parameter fails. String parameter setting is not implemented despite string current-parameter support.

## Dependencies
Touches font-directory cache APIs, memory GC status/configuration, stack limits, token scanner options, password helpers, dictionary parameter lists, and current interpreter context fields.
