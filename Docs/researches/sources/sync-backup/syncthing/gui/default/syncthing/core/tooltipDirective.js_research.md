# sources/sync-backup/syncthing/gui/default/syncthing/core/tooltipDirective.js

## Purpose
This small AngularJS directive activates Bootstrap tooltip behavior on elements carrying the `tooltip` attribute. It is an adapter between Angular templates and jQuery/Bootstrap's tooltip plugin.

## Important APIs, Control Flow, And State
The directive is registered as `tooltip` on the `syncthing.core` module, restricted to attributes, and defines only a `link` function. On link, it calls `$(element).tooltip()`. It does not define isolate scope, watchers, or controller state. All tooltip content and behavior are supplied through element attributes and Bootstrap's plugin state.

## Dependencies And Integration Points
It depends on jQuery and Bootstrap tooltip being loaded before the directive runs. It is consumed by GUI templates that use `tooltip` attributes and expect Bootstrap's `data-original-title` and tooltip lifecycle behavior.

## Risks And Test Signals
The directive does not clean up tooltips on scope destruction, which can matter if tooltipped elements are frequently created and destroyed. It also assumes Bootstrap's jQuery plugin API, so Bootstrap upgrades can break it. Test signals are simple directive tests or GUI smoke tests that verify tooltips initialize and do not throw during route/template changes.
