# sources/sync-backup/syncthing/gui/default/syncthing/core/modalDirective.js

## Purpose
This directive wraps Syncthing's Bootstrap modal template and adds behavior needed for nested/stacked modals, tab links inside modals, modal backdrop z-index management, body scroll restoration, and controller notification when a modal has loaded.

## Important APIs, types, and functions
It registers element directive `modal` on `syncthing.core`. The directive uses `templateUrl: 'modal.html'`, `replace: true`, `transclude: true`, and an isolate scope with string attributes `heading`, `status`, `icon`, `closeable`, and `large`. Its link function installs jQuery/Bootstrap event handlers for click, `show.bs.modal`, `hide.bs.modal`, and `hidden.bs.modal`, and calls `scope.$parent.modalLoaded()`.

## Control flow
Click handling intercepts tab anchors (`a[data-toggle="tab"]`) with hash hrefs and prevents default navigation. On show, the directive finds the highest z-index among visible modals, places the current modal above it, and after a zero-delay timeout adjusts the latest backdrop and hides older backdrops visually. On hide, it finds the next highest backdrop not associated with the closing modal and restores its visible class. On hidden, it resets the modal z-index and re-adds `modal-open` to the body if other modals remain visible. Finally, link-time calls `modalLoaded()` on the parent scope so the controller can track readiness.

## State and persistence behavior
The directive mutates DOM state: modal z-index, backdrop classes/attributes, and body classes. It does not persist application data. It depends on parent-scope state indirectly through `modalLoaded()`.

## Dependencies and integration points
Dependencies are AngularJS, jQuery, Bootstrap modal/backdrop markup/events, `modal.html`, parent controllers implementing `modalLoaded`, and templates that rely on this directive's isolate/transcluded scope composition. The inline comment warns that templates may rely on `$parent.$parent`, so scope shape is a compatibility concern.

## Risks
DOM event handlers are not explicitly removed on scope destruction, which can matter if modals are dynamically created/destroyed. Stacked modal behavior relies on Bootstrap class names and z-index defaults. Calling `scope.$parent.modalLoaded()` will throw if the parent does not provide that function. The directive uses `event.target.closest`, so very old browsers without `Element.closest` need polyfill support.

## Test signals
Browser tests should open stacked modals, close inner and outer modals, confirm backdrop visibility and body scrolling, exercise tab links inside modals, and verify parent `modalLoaded()` is called. Unit tests can mock jQuery events, but integration tests with Bootstrap are more valuable.
