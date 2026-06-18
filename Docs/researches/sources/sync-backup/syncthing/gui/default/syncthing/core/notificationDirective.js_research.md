# sources/sync-backup/syncthing/gui/default/syncthing/core/notificationDirective.js

## Purpose
This directive conditionally displays notification content when its notification ID is present in the current Syncthing configuration's unacknowledged notification list.

## Important APIs, types, and functions
It registers element directive `notification` on `syncthing.core`. The directive has an empty isolate scope, transcludes inner content, and uses template `<div class="row" ng-if="visible()"><div class="col-md-12" ng-transclude></div></div>`. The link function defines `scope.visible()` by checking `scope.$parent.config.options.unackedNotificationIDs.indexOf(attrs.id) > -1`.

## Control flow
On each digest where `visible()` is evaluated, the directive reads parent configuration and returns true when the directive's `id` attribute is in the unacknowledged list. Angular `ng-if` creates or removes the transcluded content accordingly.

## State and persistence behavior
The directive does not own state. It reflects parent configuration state. Acknowledgement and persistence of notifications happen elsewhere in controller/API code.

## Dependencies and integration points
It depends on parent scope shape: `config.options.unackedNotificationIDs` must exist and be an array. It integrates with notification templates and the controller that loads/saves Syncthing configuration.

## Risks
If config or options are unavailable during early render, `visible()` can throw. Missing `id` attributes will check for `undefined` in the array. Because it uses isolate scope but reaches into `$parent`, template relocation can break it.

## Test signals
Tests should cover visible and hidden states, missing IDs, dynamic updates to `unackedNotificationIDs`, and initial loading states where config may not yet be populated.
