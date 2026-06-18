# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/webapps/static/bootstrap-3.4.1/js/bootstrap.js

## Purpose

`bootstrap.js` is the readable Bootstrap v3.4.1 JavaScript bundle. It provides the browser-side behavior for Bootstrap components used by the Ozone/HDDS static web UI: transitions, alerts, buttons, carousel, collapse, dropdowns, modals, tooltips, popovers, scrollspy, tabs, and affix behavior.

The file is a vendor dependency, not Ozone-specific business logic. It registers a series of jQuery plugins under `$.fn.*`, adds data-API event handlers for declarative markup such as `data-toggle`, stores plugin instances in jQuery data keys like `bs.modal`, and emits Bootstrap namespaced events such as `show.bs.modal` and `hidden.bs.dropdown`.

## Important APIs, Types, And Functions

Top-level compatibility checks:

- Throws if `jQuery` is missing.
- Throws unless jQuery is at least 1.9.1 and lower than 4.

Transition support:

- `transitionEnd()` detects the browser transition-end event name.
- `$.fn.emulateTransitionEnd(duration)` triggers the transition-end event after a timeout when the native event does not fire.
- `$.support.transition` and `$.event.special.bsTransitionEnd` normalize transition events.

Component plugins:

- `Alert`: constructor, `VERSION`, `TRANSITION_DURATION`, `close`, plugin `$.fn.alert`, and `noConflict`.
- `Button`: constructor, `VERSION`, `DEFAULTS`, `setState`, `toggle`, plugin `$.fn.button`, and data API for `[data-toggle^="button"]`.
- `Carousel`: constructor, `VERSION`, `TRANSITION_DURATION`, `DEFAULTS`, `keydown`, `cycle`, `getItemIndex`, `getItemForDirection`, `to`, `pause`, `next`, `prev`, `slide`, plugin `$.fn.carousel`, and data API for controls and `[data-ride="carousel"]`.
- `Collapse`: constructor, `VERSION`, `TRANSITION_DURATION`, `DEFAULTS`, `dimension`, `show`, `hide`, `toggle`, `getParent`, `addAriaAndCollapsedClass`, `getTargetFromTrigger`, plugin `$.fn.collapse`, and data API for `[data-toggle="collapse"]`.
- `Dropdown`: constructor, `VERSION`, `getParent`, `clearMenus`, `toggle`, `keydown`, plugin `$.fn.dropdown`, and delegated document handlers for menu clicks and keyboard navigation.
- `Modal`: constructor, `VERSION`, transition constants, `DEFAULTS`, `toggle`, `show`, `hide`, `enforceFocus`, `escape`, `resize`, `hideModal`, `removeBackdrop`, `backdrop`, scrollbar/adjustment helpers, plugin `$.fn.modal`, and data API for `[data-toggle="modal"]`.
- Tooltip sanitization helpers: `DefaultWhitelist`, `SAFE_URL_PATTERN`, `DATA_URL_PATTERN`, `allowedAttribute`, and `sanitizeHtml`.
- `Tooltip`: constructor, `VERSION`, `TRANSITION_DURATION`, `DEFAULTS`, `init`, `getOptions`, `getDelegateOptions`, `enter`, `leave`, `show`, `hide`, positioning helpers, content helpers, state toggles, `destroy`, `sanitizeHtml`, plugin `$.fn.tooltip`, and `noConflict`.
- `Popover`: constructor, `VERSION`, `DEFAULTS`, inherits tooltip prototype, overrides `getDefaults`, `setContent`, `hasContent`, `getContent`, `arrow`, and registers `$.fn.popover`.
- `ScrollSpy`: constructor, `VERSION`, `DEFAULTS`, `getScrollHeight`, `refresh`, `process`, `activate`, `clear`, plugin `$.fn.scrollspy`, and data API for `[data-spy="scroll"]`.
- `Tab`: constructor, `VERSION`, `TRANSITION_DURATION`, `show`, `activate`, plugin `$.fn.tab`, and data API for `[data-toggle="tab"]`/`[data-toggle="pill"]`.
- `Affix`: constructor, `VERSION`, `RESET`, `DEFAULTS`, `getState`, `getPinnedOffset`, `checkPositionWithEventLoop`, `checkPosition`, plugin `$.fn.affix`, and data API for `[data-spy="affix"]`.

Every component follows the same jQuery plugin pattern: preserve the previous `$.fn.<name>` in `old`, assign the new plugin function, attach `.Constructor`, and expose `.noConflict()` to restore the old plugin.

## Control Flow

The file is a sequence of immediately invoked functions, each receiving `jQuery`. After the initial jQuery version guard, transition support is initialized on DOM ready. Component blocks then register constructors, plugin wrappers, no-conflict methods, and data-API listeners.

Plugin wrappers usually iterate over a jQuery collection, read an existing instance from `$(element).data("bs.<component>")`, merge defaults with element `data-*` attributes and explicit options, construct an instance if missing, and dispatch string options as method calls. Numeric carousel options are treated as slide positions. Data APIs call the plugin wrapper based on user actions or window load.

The component control flow is event-first. Components trigger cancellable start events (`show.bs.*`, `hide.bs.*`, `slide.bs.carousel`, `close.bs.alert`, etc.), stop when `event.isDefaultPrevented()` is true, mutate classes/attributes/DOM, wait for CSS transitions when applicable, and trigger completion events (`shown.bs.*`, `hidden.bs.*`, `slid.bs.carousel`, `closed.bs.alert`, etc.).

Transitions are coordinated by checking `$.support.transition` and component-specific transition durations. The code forces reflow with `offsetWidth`/`offsetHeight` before starting some transitions, binds `bsTransitionEnd`, and calls `emulateTransitionEnd` to avoid hanging when CSS events do not fire.

Data-API flow includes:

- Alert close on clicks matching `[data-dismiss="alert"]`.
- Button toggle on `[data-toggle^="button"]` plus focus/blur visual state.
- Carousel controls on `[data-slide]` and `[data-slide-to]`, plus auto-init for `[data-ride="carousel"]` on window load.
- Collapse toggle on `[data-toggle="collapse"]`, resolving targets from `data-target` or `href`.
- Dropdown open/close via document-level click and keydown handlers.
- Modal open via `[data-toggle="modal"]`, including remote content loading and focus restoration.
- Scrollspy and affix auto-init on window load.
- Tab activation via tab/pill click handlers.

## State And Persistence Behavior

Bootstrap component state is transient, browser-local, and stored in DOM, classes, attributes, timers, and jQuery data:

- Component instances are stored as `bs.alert`, `bs.button`, `bs.carousel`, `bs.collapse`, `bs.dropdown`, `bs.modal`, `bs.tooltip`, `bs.popover`, `bs.scrollspy`, `bs.tab`, and `bs.affix`.
- Alert state is primarily DOM presence and `.in` class.
- Button state uses `.active`, `aria-pressed`, input `checked`, disabled attributes, and saved `resetText`.
- Carousel state uses `paused`, `sliding`, `interval`, active item classes, indicator classes, and timer IDs.
- Collapse state uses `.collapse`, `.collapsing`, `.in`, `aria-expanded`, trigger classes, and `transitioning`.
- Dropdown state uses parent `.open`, `aria-expanded`, temporary `.dropdown-backdrop`, and focus.
- Modal state includes `isShown`, `$backdrop`, body class `modal-open`, padding adjustments, fixed-content padding data, scrollbar width, `ignoreBackdropClick`, focus handlers, and window resize handlers.
- Tooltip/popover state includes `enabled`, `timeout`, `hoverState`, `inState`, generated tip DOM, arrow DOM, viewport reference, and `aria-describedby`.
- Scrollspy stores computed offsets/targets, `activeTarget`, and `scrollHeight`.
- Affix stores `affixed`, `unpin`, and `pinnedOffset`.

The file performs no durable persistence. It does not use localStorage, cookies, sessionStorage, IndexedDB, or server calls except `Modal`'s deprecated-style `remote` option, which uses jQuery `.load()` to fetch modal content into `.modal-content`.

## Dependencies

The bundle depends on jQuery 1.9.1 or newer but below jQuery 4. It assumes a browser DOM, window/document globals, CSS classes matching Bootstrap 3.4.1, and Bootstrap CSS transition definitions for animated components. Popover explicitly requires tooltip to be registered. Tooltip/popover sanitization uses `document.implementation.createHTMLDocument` when available and falls back to returning the unsafe HTML unchanged on very old browsers lacking that API.

The code uses jQuery event delegation, data parsing, `.offset()`, `.position()`, `.one()`, `.on()`, `.off()`, `.trigger()`, `.Event()`, and `.load()`. It also uses browser layout APIs such as `getBoundingClientRect`, `offsetWidth`, `offsetHeight`, `scrollHeight`, `innerWidth`, and `SVGElement` checks.

## Integration Points

Application HTML integrates through data attributes and expected markup:

- Alerts need `.alert`, `.fade`, `.in`, and `[data-dismiss="alert"]`.
- Buttons use `.btn`, `[data-toggle="buttons"]`, radio/checkbox inputs, and loading text data attributes.
- Carousel needs `.carousel`, `.item.active`, `.carousel-indicators`, and data controls.
- Collapse needs `.collapse`, optional `.panel` parents, `data-parent`, and trigger target IDs.
- Dropdowns need `[data-toggle="dropdown"]`, parent `.dropdown`, `.dropdown-menu`, and optional `.navbar-nav`.
- Modals need `.modal`, `.modal-dialog`, `.modal-content`, and dismiss controls.
- Tooltip/popover integrate through title/content attributes, selectors, containers, template options, and trigger settings.
- Scrollspy expects nav selectors built from `options.target + " .nav li > a"`.
- Tabs/pills need tab links and target panes.
- Affix expects scroll targets and offset configuration.

Programmatic integration is through `$(element).<plugin>(optionsOrCommand)`, Bootstrap event listeners, and `noConflict` when another plugin owns the same jQuery method.

## Risks And Edge Cases

- Vendor code is fixed at Bootstrap 3.4.1. It is not compatible with jQuery 4 and may be increasingly brittle in modern front-end stacks.
- Tooltip/popover HTML sanitization is enabled by default, but when `sanitize: false` or a custom template/display path is used, content becomes XSS-sensitive. On very old browsers without `createHTMLDocument`, `sanitizeHtml` returns input unchanged.
- The sanitizer explicitly strips `sanitize`, `whiteList`, and `sanitizeFn` data attributes from tooltip options, so security-sensitive sanitizer configuration cannot be supplied through markup.
- Modal `remote` uses jQuery `.load()` and injects remote HTML into `.modal-content`; pages using it need server-side trust boundaries and error handling.
- Selector extraction from `href`/`data-target` is built for old browser compatibility. Malformed selectors can still trigger jQuery selector errors or no-op behavior in page code.
- Transition-dependent components can appear stuck if CSS duration mismatches the hard-coded JavaScript duration, though `emulateTransitionEnd` mitigates missing events.
- Global delegated handlers can interact unexpectedly with nested menus, forms inside dropdowns, focus traps in modals, and dynamically removed elements.
- Scrollspy and affix depend on layout measurements; hidden elements, late-loading content, dynamic document height changes, and nested scroll containers require refresh or update calls.
- `Button.setState` is deprecated in later Bootstrap lines and mutates HTML content directly; data-driven loading text should not contain untrusted HTML.

## Test Signals

Useful signals include:

- Asset smoke test: page loads with jQuery in the supported range and no plugin registration errors.
- Data API test: markup-only controls for alerts, buttons, carousel, collapse, dropdown, modal, tab, scrollspy, and affix behave without explicit JavaScript.
- Event contract test: cancellable `show`/`hide`/`close`/`slide` events can prevent mutations, while completion events fire after synchronous and transition paths.
- Accessibility state test: `aria-expanded`, `aria-pressed`, `aria-describedby`, focus restoration, modal focus trapping, and disabled states update correctly.
- Transition test: fade/slide components complete with and without CSS transition support.
- Tooltip/popover sanitization test: unsafe HTML is stripped under default options and custom `sanitizeFn` is honored when passed programmatically.
- Dynamic DOM test: destroying/removing tooltips, popovers, modals, collapses, and affixed elements does not leave active handlers or visible overlays.
- Layout-sensitive test: scrollspy refresh and affix position changes work after content height changes and window resize.
