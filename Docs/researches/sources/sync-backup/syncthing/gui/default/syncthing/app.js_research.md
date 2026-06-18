# sources/sync-backup/syncthing/gui/default/syncthing/app.js

## Purpose
This file bootstraps the main AngularJS `syncthing` module and defines shared browser-global utilities used throughout the Syncthing GUI. It wires translation and locale services, configures XSRF header/cookie names, and exposes helper functions for device/folder ordering, object mapping, debouncing, tree-building, and unit-prefix formatting.

## Important APIs, types, and functions
The module declaration creates `angular.module('syncthing', ['angularUtils.directives.dirPagination', 'pascalprecht.translate', 'ngSanitize', 'syncthing.core'])`. Global constants include `urlbase = 'rest'`, `authUrlbase = 'rest/noauth/auth'`, and `shortIDStringLength = 7`. The config block sets angular-translate static files loader prefix/suffix, English fallback, locale provider defaults, async HTTP digest behavior, and metadata-derived CSRF names. Utility functions include `deviceCompare`, `folderCompare`, `deviceMap`, `deviceList`, `folderMap`, `folderList`, `isEmptyObject`, `debounce`, `buildTree`, and `unitPrefixed`.

## Control flow
During Angular config, the app sets translation sanitization to `escape`, registers `assets/lang/lang-*.json`, sets available/default locales, and enables `$httpProvider.useApplyAsync(true)`. If `window.metadata` is missing, setup returns early because unauthenticated pages cannot configure device-specific CSRF names. Device/folder helper functions convert arrays to ID-keyed maps and back with stable sorting. `debounce` invokes immediately on the first call, schedules a trailing call when calls occur within the wait window, and retains the last arguments/context. `buildTree` converts a path-to-data object into a nested tree of folder and file nodes. `unitPrefixed` formats metric or binary quantities up to tera-prefixes using locale-aware number formatting.

## State and persistence behavior
Most helpers are pure except `debounce`, which holds timeout, timestamp, and trailing-call state in closure variables. Angular configuration mutates provider state. CSRF names depend on global `metadata.deviceIDShort`, which comes from the server-rendered page. No local storage is written here, but `LocaleServiceProvider` receives the locale list for later persisted selection.

## Dependencies and integration points
Dependencies include AngularJS, angular-translate, ngSanitize, dirPagination, jQuery, global `validLangs`, browser `metadata`, and Bootstrap-oriented templates/controllers that use the globals. Filters `binaryFilter.js` and `metricFilter.js` call `unitPrefixed`. Controllers use `urlbase`, `authUrlbase`, device/folder map/list helpers, `buildTree` for version restore views, and `shortIDStringLength` for device ID display consistency.

## Risks
Because many utilities are browser globals, load order is critical and refactoring can break filters/controllers without explicit imports. The config early return for missing metadata must preserve unauthenticated login behavior. `deviceCompare` and `folderCompare` return booleans for greater-than cases rather than strictly `1`, relying on JavaScript sort coercion. `buildTree` uses loose equality for folder title comparison and does not sort generated children. `unitPrefixed` only reaches tera units, so very large values remain represented as large tera numbers.

## Test signals
Unit tests should cover sorting by label/name/ID, map/list round trips, debounce leading and trailing calls, path tree construction, and metric/binary formatting at threshold boundaries. Browser tests should verify unauthenticated pages do not require metadata, authenticated requests send the metadata-derived CSRF header/cookie, translations load from the expected paths, and binary/metric filters render locale-aware strings.
