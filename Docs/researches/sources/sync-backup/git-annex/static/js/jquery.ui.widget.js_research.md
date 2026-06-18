# sources/sync-backup/git-annex/static/js/jquery.ui.widget.js

Purpose: vendored jQuery UI Widget Factory 1.10.4, providing the base class and plugin bridge used by jQuery UI widgets such as sortable. It standardizes widget construction, inheritance, option management, event binding, teardown, and effect helpers.

Important APIs/types/functions: exports `$.widget`, `$.widget.extend`, `$.widget.bridge`, and base constructor `$.Widget`. Base prototype methods include `_createWidget`, `_getCreateOptions`, `_create`, `_init`, `destroy`, `widget`, `option`, `_setOptions`, `_setOption`, `enable`, `disable`, `_on`, `_off`, `_delay`, `_hoverable`, `_focusable`, `_trigger`, `_show`, and `_hide`. It also wraps `$.cleanData` to trigger `remove` before element cleanup.

Control flow: `$.widget` parses `namespace.name`, creates or redefines a constructor, sets up `_super`/`_superApply` wrappers for function properties, builds the prototype from the base plus proxied prototype, updates child constructors on redefinition, and installs a jQuery plugin bridge. The bridge dispatches string method calls to existing instances and object calls to initialization or option update. `_createWidget` binds the instance to an element, merges defaults with create options and caller options, sets document/window references, calls `_create`, fires `create`, and calls `_init`.

State/persistence behavior: state is per-widget instance and stored with jQuery data under `widgetFullName`, legacy widget name, and camel-case compatibility keys. It tracks `uuid`, `eventNamespace`, `options`, `bindings`, `hoverable`, and `focusable`. Destruction unbinds namespaced events, removes disabled/hover/focus classes, and clears data. No browser storage or server persistence is used.

Dependencies/integration: depends on jQuery core features including data, events, selectors, `$.Event`, `$.Callbacks`-style callbacks, delegation, and optional `$.effects`. It is the integration substrate for all widgets in this vendored UI stack.

Risks/test signals: method dispatch intentionally blocks private `_` methods and errors before initialization. Option handling must preserve nested option semantics and avoid sharing prototype options. Tests should cover widget inheritance, `_super` calls, redefinition of base widgets, delegated events with disabled checks, automatic destroy on remove, callback cancellation from `_trigger`, and fallback show/hide behavior when effects are absent.
