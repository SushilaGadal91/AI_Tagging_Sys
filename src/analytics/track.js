// src/analytics/track.js
export function track(eventName, params = {}) {
  const s = window && window.s;
  if (!s) {
    // eslint-disable-next-line no-console
    console.warn('[track] Adobe AppMeasurement `s` not found. Event:', eventName, params);
    return;
  }
  const isPageView = !!params.__pv;
  const { __pv, events, ...rest } = params;
  const prevLinkTrackVars = s.linkTrackVars;
  const prevLinkTrackEvents = s.linkTrackEvents;
  try {
    const varNames = [];
    for (const [k, v] of Object.entries(rest)) {
      if (/^(eVar|prop)\d+$/i.test(k)) { s[k] = v; varNames.push(k); }
      else if (k === 'pageName') { s.pageName = v; varNames.push('pageName'); }
    }
    if (isPageView) {
      if (events) s.events = events; // e.g., 'event10'
      s.t();               // page view call
      s.clearVars();       // prevent bleed to next hit
      return;
    }
    // Link tracking (CTA/click)
    s.linkTrackVars = varNames.concat('events').join(',');
    if (events) s.linkTrackEvents = events;
    s.events = events || '';
    s.tl(true, 'o', eventName);  // 'o' = custom link, name = eventName
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error('track error', e);
  } finally {
    s.linkTrackVars = prevLinkTrackVars;
    s.linkTrackEvents = prevLinkTrackEvents;
  }
}
