<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/swagger-ui-standalone-preset.js -->
# sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/swagger-ui-standalone-preset.js

## Purpose
This is a vendored, minified Swagger UI standalone preset bundle for the Ozone documentation theme. It exposes `SwaggerUIStandalonePreset` through a UMD wrapper so the same artifact can be consumed by CommonJS, AMD, browser globals, or the local Swagger UI initialization code used by the docs site.

## Important APIs, Types, And Functions
- The top-level UMD wrapper exports `SwaggerUIStandalonePreset`.
- The preset array registers Swagger UI plugins for the standalone view, including `Topbar`, `Logo`, `StandaloneLayout`, `ErrorBoundary`, `Fallback`, and wrapping for `Topbar`, `StandaloneLayout`, and `onlineValidatorBadge`.
- The bundled config state plugin exposes actions equivalent to config update/toggle behavior and selectors such as `getLocalConfig`.
- `getLocalConfig` returns a default YAML configuration containing the Petstore spec URL, `#swagger-ui` DOM target, and the public Swagger validator URL.
- The bundle includes minified third-party runtime code for React components, object helpers, URL/config parsing, YAML parsing, and browser polyfills such as Buffer/base64 helpers.

## Control Flow
The file initializes immediately when loaded. The wrapper detects the module system, invokes the bundled factory, and returns a preset array. Swagger UI later consumes the preset by invoking its plugin factories. Those factories register components, state plugins, selectors, reducers, and wrapper components. Config loading flows through a fetch action that downloads a YAML config, parses it, updates loading status on failure, clears the URL, and logs errors to the browser console.

## State And Persistence
The file does not write durable application state. It contributes runtime Redux-like Swagger UI state through config reducers and selectors once the docs page loads. Browser-visible state includes config values, loading status, wrapped component error state, and rendered Swagger UI component state. Persistence is limited to the static asset itself and any browser cache of the generated documentation site.

## Dependencies And Integration Points
This asset lives beside `swagger-ui-bundle.js`, `swagger-ui.css`, `recon-api.yaml`, and favicon assets under the Ozone Hugo theme static tree. It integrates with the generated documentation pages that mount Swagger UI into `#swagger-ui`. It depends on the compatible Swagger UI bundle/runtime being loaded by the page, browser APIs such as `fetch`, and the static OpenAPI YAML resource. The source map comment references `swagger-ui-standalone-preset.js.map`, but that map is not present in the same directory.

## Risks And Edge Cases
Because the bundle is minified and vendored, local patches are difficult to review and are likely to be overwritten by Swagger UI upgrades. The default Petstore URL and public validator URL can leak through if page initialization does not override them with Ozone-specific config. The missing source map makes browser debugging harder. Security-sensitive behavior, including URL sanitization and YAML parsing, should track upstream Swagger UI versions rather than local edits. Any version mismatch between this preset, `swagger-ui-bundle.js`, and `swagger-ui.css` can break component names or plugin contracts at runtime.

## Test Signals
Useful validation signals include loading the generated documentation Swagger page, confirming the Ozone/OpenAPI spec renders in `#swagger-ui`, checking that the top bar and standalone layout render without console errors, verifying no network request goes to the default Petstore spec during normal Ozone docs usage, and confirming static site packaging includes this file together with compatible Swagger UI assets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/docs/themes/ozonedoc/static/swagger-resources/swagger-ui-standalone-preset.js -->
