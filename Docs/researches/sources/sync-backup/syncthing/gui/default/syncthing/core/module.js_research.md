# sources/sync-backup/syncthing/gui/default/syncthing/core/module.js

## Purpose
This file declares the AngularJS `syncthing.core` module that hosts shared Syncthing GUI services, filters, and directives.

## Important APIs, types, and functions
The only API is `angular.module('syncthing.core', []);`, creating the module with no Angular module dependencies.

## Control flow
There is no runtime branching. The declaration must execute before files that call `angular.module('syncthing.core')` to register components.

## State and persistence behavior
The Angular module registry is mutated by this declaration. No application state is persisted.

## Dependencies and integration points
It depends on AngularJS being loaded. `app.js` depends on this module by listing `'syncthing.core'` in the main `syncthing` module dependencies. All core files in this subset register against this module.

## Risks
Load order is critical: if registration files load before this declaration, Angular throws "module not available"; if this declaration runs after registrations, it recreates the module and discards previously registered components. Any future dependencies must be added here carefully.

## Test signals
Bundle/order tests should ensure `module.js` precedes core component registrations and `app.js` can bootstrap the main module. A simple Angular injector smoke test can assert registered filters/services/directives are available.
