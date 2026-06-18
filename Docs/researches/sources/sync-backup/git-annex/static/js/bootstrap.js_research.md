<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/bootstrap.js -->
# sources/sync-backup/git-annex/static/js/bootstrap.js

Purpose: vendored Bootstrap v3.1.1 JavaScript bundle used by git-annex's static web UI. It adds jQuery plugins for transitions, alerts, buttons, carousel, collapse, dropdowns, modals, tooltips, popovers, scrollspy, tabs, and affix behavior.

Important modules and APIs: the file requires global `jQuery` and registers plugins on `$.fn`: `alert`, `button`, `carousel`, `collapse`, `dropdown`, `modal`, `tooltip`, `popover`, `scrollspy`, `tab`, and `affix`. Each plugin stores component instances under `data('bs.<component>')`, exposes a `Constructor`, and implements `noConflict`. `transition.js` detects CSS transition end event names and adds `$.fn.emulateTransitionEnd(duration)`.

Control flow: each Bootstrap module is wrapped in an IIFE receiving `jQuery`. Data APIs bind delegated handlers on `document` or `window load`: alert dismissal, button toggles, carousel controls/auto-start, collapse toggles, dropdown clicks/keyboard navigation, modal launchers, scrollspy initialization, tab clicks, and affix initialization. Programmatic API calls go through jQuery plugin dispatch, creating an instance if needed and invoking string-named methods.

Component state: components persist runtime state in jQuery data and instance fields. Carousel tracks `paused`, `sliding`, `interval`, `$active`, and `$items`; Collapse tracks `transitioning`; Dropdown uses parent `.open` classes and mobile backdrops; Modal tracks `isShown` and `$backdrop` and toggles `body.modal-open`; Tooltip/Popover track enabled state, timeout, hover state, generated tip/arrow nodes, title/content, and placement; ScrollSpy tracks offsets, targets, and active target; Affix tracks `affixed`, `unpin`, and pinned offset.

Dependencies and integration points: jQuery APIs for events, data, DOM traversal, effects, offset/position, AJAX `.load` for modal remotes, and CSS classes from Bootstrap 3.1.1. Browser integration includes `document`, `window`, transition events, keyboard events, focus handling, and scroll state.

Risks: this is an old Bootstrap release. Tooltip and popover support `html: true` and template/content injection without the later sanitizer facilities, so callers must not pass untrusted HTML. Modal `remote` loads arbitrary URLs into `.modal-content` through jQuery. Selector construction from `href`/`data-target` can be fragile with unusual IDs. Global delegated handlers and jQuery data can leak if DOM nodes are removed without plugin cleanup. Accessibility behavior reflects Bootstrap 3.1.1 and is limited compared with modern components.

Test signals: browser/UI tests should cover every data API and programmatic plugin path, transition/no-transition branches, modal focus trapping and backdrop behavior, dropdown keyboard navigation, tooltip/popover placement including `auto`, scrollspy/affix on scroll, and the git-annex web pages that depend on these plugins. Security tests should verify no untrusted HTML reaches tooltip/popover/modal remote options.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/static/js/bootstrap.js -->
