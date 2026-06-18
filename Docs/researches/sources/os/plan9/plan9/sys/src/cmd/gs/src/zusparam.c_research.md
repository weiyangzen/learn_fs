# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zusparam.c

## Purpose
Implements Ghostscript user and system parameter operators, including password checks, VM/font/cache limits, scanner option updates, and parameter retrieval.

## Public Surface
- `set_user_params`: exported for context switching.
- Registered operators: `.currentsystemparams`, `.currentuserparams`, `.getsystemparam`, `.getuserparam`, `.setsystemparams`, `.setuserparams`, and Level 2 `.checkpassword`.

## Implementation Notes
- Parameter definitions are described by small structs for long, bool, and string parameters.
- System long params include `BuildTime`, `MaxFontCache`, `CurFontCache`, `Revision`, `MaxGlobalVM`.
- System bool/string params include `ByteOrder` and `RealFormat`.
- User long params include `JobTimeout`, font cache controls, stack maxima, `MaxLocalVM`, `VMReclaim`, `VMThreshold`, `WaitTimeout`, `MinScreenLevels`, `AlignToPixels`, and `GridFitTT`.
- User bool params include `AccurateScreens`, `UseWTS`, and `LockFilePermissions`.
- `.checkpassword` compares supplied password against `StartJobPassword` and `SystemParamsPassword`.
- `.setsystemparams` validates `SystemParamsPassword`, can update start/system passwords subject to `LockFilePermissions`, then applies writable system params.
- `.setuserparams` applies user params and refreshes cached scanner options with `ztoken_scanner_options`.
- `current_param_list` writes matching parameter name/value pairs onto the operand stack; `currentparam1` filters by name and returns one value or `undefined`.

## Dependencies
Uses font directory/cache APIs, GC/VM status APIs, parameter-list readers/writers, dictionaries, token scanner options, stack maxima, halftone/user rendering options, and VM control helpers from `ivmem2.h`.

## Risks and Notes
- `setparams` does not roll back partial changes if a later parameter fails.
- `LockFilePermissions` can only be enabled once; disabling while locked returns `invalidaccess`.
- String/string-array parameter setting is explicitly not implemented.
- Filesystem relevance: indirect only through `LockFilePermissions`, which affects later file permission behavior.
