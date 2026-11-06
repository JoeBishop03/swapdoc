// Visitor statistics with Azure Application Insights, set up to be cookie-free:
// no cookies, no local storage. Visitors are grouped by an anonymous ID made on
// the server that changes every day. Records: page views, where visitors came
// from, device type, time spent on each page and conversion results.
(function () {
  var me = document.currentScript;
  var cs = me && me.getAttribute('data-cs');
  var vid = me && me.getAttribute('data-vid');
  if (!cs || !window.Microsoft || !Microsoft.ApplicationInsights) return; // e.g. blocked by an ad blocker

  var ai = new Microsoft.ApplicationInsights.ApplicationInsights({
    config: {
      connectionString: cs,
      disableCookiesUsage: true,
      isStorageUseDisabled: true,
      enableSessionStorageBuffer: false,
      disableAjaxTracking: true,
      disableFetchTracking: true,
      enableAutoRouteTracking: false,
      // Use pagehide/visibilitychange only. An "unload" listener stops browsers
      // keeping the page for an instant Back button, and is deprecated.
      disablePageUnloadEvents: ['unload', 'beforeunload']
    }
  });
  ai.loadAppInsights();

  // Use the daily anonymous ID as both the visitor and the visit.
  ai.addTelemetryInitializer(function (item) {
    item.tags = item.tags || {};
    item.tags['ai.user.id'] = vid;
    item.tags['ai.session.id'] = vid;
  });
  ai.setAuthenticatedUserContext(vid, null, false);

  function source() {
    var p = new URLSearchParams(location.search);
    if (p.get('utm_source')) return p.get('utm_source').toLowerCase();
    if (p.get('gclid')) return 'google ads';
    if (!document.referrer) return 'direct';
    try {
      var h = new URL(document.referrer).hostname.replace(/^www\./, '');
      if (h === location.hostname.replace(/^www\./, '')) return 'internal';
      return h;
    } catch (e) { return 'unknown'; }
  }
  function device() {
    var coarse = window.matchMedia && matchMedia('(pointer: coarse)').matches;
    if (!coarse) return 'Desktop';
    return Math.min(screen.width, screen.height) >= 600 ? 'Tablet' : 'Mobile';
  }

  var page = location.pathname;
  ai.trackPageView({
    name: page,
    uri: location.origin + location.pathname,
    properties: { source: source(), device: device(), title: document.title }
  });

  window.sdTrack = function (name, props) {
    props = props || {};
    props.page = page;
    ai.trackEvent({ name: name, properties: props });
  };

  // Time actually spent looking at the page (paused while the tab is hidden).
  var shownAt = document.visibilityState === 'visible' ? Date.now() : 0;
  var spent = 0;
  function pause() {
    if (shownAt) { spent += Date.now() - shownAt; shownAt = 0; }
    var secs = Math.round(spent / 1000);
    spent = 0;
    if (secs < 1) return;
    ai.trackEvent({ name: 'engaged', properties: { page: page }, measurements: { seconds: Math.min(secs, 1800) } });
    ai.flush(false); // sent with sendBeacon so it survives the page closing
  }
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') pause();
    else shownAt = Date.now();
  });
  window.addEventListener('pagehide', pause);
})();
