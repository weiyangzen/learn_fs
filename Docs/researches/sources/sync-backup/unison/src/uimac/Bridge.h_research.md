# sources/sync-backup/unison/src/uimac/Bridge.h

Purpose: Objective-C bridge header exposing C-callable entry points for Unison’s macOS UI integration.

Important APIs: `cocoaPut`, `cocoaGet`, `cocoaInit`, `cocoaRunning`, `cocoaStop`, `cocoaSystem`, `cocoaOpenFile`, `cocoaShowPreference`, `cocoaSelect`, `cocoaSetToolbarItems`, `cocoaBeginSheet`, `cocoaEndSheet`, `cocoaSetEnabled`, `cocoaSetVisible`, `cocoaSetModified`, `cocoaSetDefaultButton`, `cocoaSetTitle`, `cocoaSetString`, `cocoaAppendString`, `cocoaSetContentSize`, `cocoaSetFrameAutosaveName`, `cocoaSetAutosaveTableColumns`, `cocoaSetValidateMenuItem`, `cocoaSetAction`, and `cocoaSetDoubleAction`.

Control flow: declarations only. The implemented bridge likely lets OCaml/C code address Cocoa objects by string identifiers, set UI state, run modal sheets, invoke actions, and exchange values.

State/persistence: no state in the header, but declared functions imply mutation of Cocoa control state, toolbar/menu configuration, window autosave names, and application lifecycle state.

Dependencies/integration: Objective-C/C boundary for `uimac`, Cocoa runtime implementation files, and macOS app build (`make macui` and CI app packaging).

Risks: stringly typed object/action identifiers are easy to mistype and may fail at runtime. Header/implementation drift can break linkage. UI calls must run on the correct Cocoa thread in the implementation.

Test signals: macOS `make macui`, app launch, UI smoke tests for controls/actions/sheets/toolbars, and linker checks that every declared symbol is implemented.
