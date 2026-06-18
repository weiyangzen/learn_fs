<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/Bridge.m -->
# sources/sync-backup/unison/src/uimac/Bridge.m

Source read: complete file, 418 lines, 15625 bytes, sha256 `81368b8837a9a742`.

Purpose: Objective-C/C bridge between the Cocoa UI and Unison's OCaml core. It starts the OCaml runtime off the AppKit main thread, exposes `ocamlCall()`, and marshals C/Objective-C calls through an OCaml-owned callback thread so value allocation and field access happen while the OCaml runtime lock is held.

Important APIs/types/functions: `Bridge +startup:`, `-_ocamlStartup:`, `bridgeThreadWait`, `ocamlCall`, `_passCall`, `getField`, and `OCamlValue` are the key surfaces. The type signature alphabet is `x`, `i`, `s`, `S`, `N`, and `@`, with a hard limit of three converted arguments. It also installs an `NSExceptionHandler` delegate and registers OCaml global roots for wrapped values.

Implementation inventory: discovered Objective-C/C callback methods include `_ocamlStartup, startup, exceptionHandler, bridgeThreadWait, count, getField, value, dealloc`.

Control flow: Startup saves argv, detaches `_ocamlStartup:`, waits on `init_cond`, runs `caml_startup`, then calls the OCaml `callbackThreadCreate` entry. Cocoa callers populate a stack `CallState`; `_passCall` publishes it under `global_call_lock`, waits for `_RetState`, and rethrows OCaml exceptions as `NSException`. `bridgeThreadWait` loops forever, enters a blocking section while idle, converts arguments, invokes the named OCaml callback or field access, converts the result, and signals the waiting caller.

State and persistence behavior: The bridge owns global mutex/condition pairs, `_CallState`, `_RetState`, `doneInit`, `the_argv`, and OCaml global roots held by `OCamlValue`. Results that become Objective-C objects are autoreleased on the caller side. There is no durable persistence, but thread state is process-wide and singleton-style.

Dependencies and integration points: Depends on Cocoa, ExceptionHandling, pthreads, the OCaml C runtime headers, OCaml named values `callbackThreadCreate` and `unisonExnInfo`, and every UI file that uses `ocamlCall` or `OCamlValue`.

Risks: The single global call slot serializes all OCaml calls and would deadlock if a caller re-enters incorrectly. Varargs signatures are unchecked at compile time, only three arguments are supported, exception strings are leaked with `strdup`, and unsafe legacy callback code remains compiled out. Incorrect use of `OCamlValue value` outside the bridge thread can race the OCaml GC.

Test signals: Exercise GUI startup, non-GUI startup, password callbacks, table updates, diff/status callbacks, and exception paths. Static checks should verify all `ocamlCall` signatures against OCaml registrations and that every `OCamlValue` field access goes through `getField`.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/Bridge.m -->
