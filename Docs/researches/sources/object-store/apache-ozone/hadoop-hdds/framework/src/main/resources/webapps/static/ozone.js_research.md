# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/webapps/static/ozone.js

## Purpose

This file defines the AngularJS front-end module for the legacy HDDS/Ozone web UI. It wires routes for the main page, RPC metrics page, and configuration page, and provides components for overview JMX data, JVM parameters, RPC metric visualization, tabs, navigation, and configuration filtering.

## Important APIs, Types, And Functions

The main Angular module is `ozone`, with dependencies on `nvd3` and `ngRoute`. Components include `overview`, `jvmParameters`, `rpcMetrics`, `rpcMetric`, `tabs`, `pane`, `navmenu`, and `config`. `isIgnoredJmxKeys()` filters JMX metadata keys from metrics output. The `rpcMetric` controller builds grouped structures for latency percentiles, success/failure counters, operation counts, averages, and unmatched metrics. The `config` controller calls `conf?cmd=getOzoneTags` and `conf?cmd=getPropertyByTag`.

## Control Flow

The route provider maps `/`, `/metrics/rpc`, and `/config` to either static templates or component tags. Components load server-side JSON via `$http` after instantiation. RPC metrics are collected from the Hadoop JMX endpoint and reshaped whenever `jmxdata` changes. Configuration first loads tags, removes legacy excluded tags, loads all tagged configuration entries, normalizes them into an array, and applies component/tag filters and sorting.

## State And Persistence

State is entirely browser-side controller state: selected tabs, selected config tags, normalized config arrays, JMX data, and a docs-link availability flag. There is no local persistence. The source depends on server endpoints for durable configuration and metrics.

## Dependencies And Integration Points

The UI integrates with Hadoop JMX endpoints, the HDDS configuration servlet, `static/templates/*.html`, AngularJS, ngRoute, nvd3, d3 formatting, and optional `docs/index.html`.

## Risks

The file uses older AngularJS idioms and loose equality. `Object.values` can be a browser compatibility risk in very old environments. Configuration filtering mutates `ctrl.configs` from the normalized master map, so missed calls to `reloadConfig()` can compound filters. JMX metric grouping depends on name regexes, so renamed metrics silently fall into `others`.

## Test Signals

Useful signals include loading all routes, successful JMX and `conf` requests, visual RPC percentile charts, config sorting and filtering by component/tag, docs-link presence/absence behavior, and browser console checks for missing templates or unsupported JavaScript APIs.
