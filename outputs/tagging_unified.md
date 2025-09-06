# Tagging Suggestions Report

- **Excel**: `/mnt/c/Users/sgadal/AppSelector/agentic_tagging_system/TechSpec_Tagging.xlsx`
- **Repo**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js`
- **Items**: 10

## Page: BillType
### KPI: [BillType] Page view recorded when BillType page loads
- **Action**: `view`
- **Adobe**: var=`eVar10`, value=`PageView_BillType`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:3`  (confidence 0.85)
- **Why here**: The BillType component is responsible for rendering the BillType page, making it the appropriate location to track page views.
- **Event**: `pageView`
- **Params:**
```json
{
  "__pv": true,
  "pageName": "PageView_BillType",
  "eVar10": "PageView_BillType"
}
```
- **Implementation**: Ensure that the track function is called when the component mounts to capture the page view.
- **Risks**: Potential for duplicate tracking if not managed correctly, May not capture if the component is not mounted properly

```jsx
   1: import React from 'react';
   2: import { useNavigate } from 'react-router-dom';
   3: export default function BillType(){
   4:   const nav=useNavigate();
   5:   const pick=(type)=>nav('/enter-number',{state:{billType:type}});
   6:   return(<div className="screen"><div className="page">
   7:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
   8:     <h1 className="hero">What type of bill do you want to pay?</h1>
   9:     <div className="grid-2 compact">
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { useEffect } from 'react';
```

_Hook (page view):_
```jsx
useEffect(() => { track('pageView', { __pv: true, pageName: 'PageView_BillType', eVar10: 'PageView_BillType' }); }, []);
```
### KPI: [BillType] Utilization of 'Home Internet' option
- **Action**: `select`
- **Adobe**: var=`eVar12`, value=`Select_BillType_HomeInternet`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:11`  (confidence 0.85)
- **Why here**: The event handler for selecting the 'Home Internet' option is located in the BillType component.
- **Event**: `selectBillType`
- **Params:**
```json
{
  "eVar12": "Select_BillType_HomeInternet",
  "pageName": "BillType"
}
```
- **Implementation**: Track the selection of the 'Home Internet' option when the corresponding tile is clicked.
- **Risks**: Event may not fire if the click handler is not correctly implemented., Potential for duplicate events if not properly managed.

```jsx
   5:   const pick=(type)=>nav('/enter-number',{state:{billType:type}});
   6:   return(<div className="screen"><div className="page">
   7:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
   8:     <h1 className="hero">What type of bill do you want to pay?</h1>
   9:     <div className="grid-2 compact">
  10:       <div className="tile big" onClick={()=>pick('Mobile')}><span>Mobile</span></div>
  11:       <div className="tile big" onClick={()=>pick('Home Internet')}><span>Home Internet</span></div>
  12:     </div></div></div>);
  13: }
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from "../analytics/track.js";
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
data-analytics-id="select_billtype_homeinternet"
onClick={(e) => {
  track("selectBillType", {
  "eVar12": "Select_BillType_HomeInternet",
  "pageName": "BillType"
});
  /* originalOnClick?.(e); */
}}
>
  ...
</YourElement>
```

_Alternative wrapper (if preserving existing handler):_
```js
/* If the element uses a named handler like onClick={handleClick}, wrap it: */
const _origHandleClick = typeof handleClick === 'function' ? handleClick : null;
const handleClickTracked = (e) => {
  track("selectBillType", {
  "eVar12": "Select_BillType_HomeInternet",
  "pageName": "BillType"
});
  if (_origHandleClick) return _origHandleClick(e);
};
/* then use: onClick={handleClickTracked} */
```
### KPI: [BillType] Utilization of 'Mobile' option
- **Action**: `select`
- **Adobe**: var=`eVar11`, value=`Select_BillType_Mobile`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:10`  (confidence 0.85)
- **Why here**: The code contains a clickable JSX element for the 'Mobile' option, making it suitable for tracking the selection action.
- **Event**: `select_bill_type`
- **Params:**
```json
{
  "eVar11": "Select_BillType_Mobile",
  "events": "event1",
  "__pv": false,
  "pageName": "BillType"
}
```
- **Implementation**: Track the selection of the 'Mobile' bill type option.
- **Risks**: Event may not fire if navigation fails, User may not click the option

```jsx
   4:   const nav=useNavigate();
   5:   const pick=(type)=>nav('/enter-number',{state:{billType:type}});
   6:   return(<div className="screen"><div className="page">
   7:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
   8:     <h1 className="hero">What type of bill do you want to pay?</h1>
   9:     <div className="grid-2 compact">
  10:       <div className="tile big" onClick={()=>pick('Mobile')}><span>Mobile</span></div>
  11:       <div className="tile big" onClick={()=>pick('Home Internet')}><span>Home Internet</span></div>
  12:     </div></div></div>);
  13: }
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from "../analytics/track.js";
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
data-analytics-id="select_billtype_mobile"
onClick={(e) => {
  track("select_bill_type", {
  "eVar11": "Select_BillType_Mobile",
  "events": "event1",
  "__pv": false,
  "pageName": "BillType"
});
  /* originalOnClick?.(e); */
}}
>
  ...
</YourElement>
```

_Alternative wrapper (if preserving existing handler):_
```js
/* If the element uses a named handler like onClick={handleClick}, wrap it: */
const _origHandleClick = typeof handleClick === 'function' ? handleClick : null;
const handleClickTracked = (e) => {
  track("select_bill_type", {
  "eVar11": "Select_BillType_Mobile",
  "events": "event1",
  "__pv": false,
  "pageName": "BillType"
});
  if (_origHandleClick) return _origHandleClick(e);
};
/* then use: onClick={handleClickTracked} */
```
## Page: EnterNumber
### KPI: [EnterNumber] Page view recorded when EnterNumber page loads
- **Action**: `view`
- **Adobe**: var=`eVar30`, value=`PageView_EnterNumber`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/EnterNumber.js:4`  (confidence 0.85)
- **Why here**: The EnterNumber component is the main page that will trigger the page view event upon loading.
- **Event**: `pageView`
- **Params:**
```json
{
  "__pv": true,
  "pageName": "PageView_EnterNumber",
  "eVar30": "PageView_EnterNumber"
}
```
- **Implementation**: Add a useEffect hook to track the page view when the component mounts.
- **Risks**: Ensure track function is correctly implemented, Check for potential duplicate page view tracking

```jsx
   1: import React, {useState} from 'react';
   2: import { useLocation, useNavigate } from 'react-router-dom';
   3: import Keypad from '../components/Keypad.js';
   4: export default function EnterNumber(){
   5:   const nav=useNavigate(); const {state}=useLocation(); const billType=state?.billType||'Mobile';
   6:   const [value,setValue]=useState(''); const maxLen=billType==='Mobile'?10:12;
   7:   const onKey=(k)=>{ if(k==='Clear') return setValue(''); if(k==='⌫') return setValue(v=>v.slice(0,-1)); if(/^\d$/.test(k)) setValue(v=>(v+k).slice(0,maxLen)); };
   8:   const onSubmit=(e)=>{ e.preventDefault(); if(value.length<Math.min(6,maxLen)) return; alert(`Mock submit for ${billType}: ${value}`); };
   9:   return(<div className="screen"><div className="page">
  10:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { useEffect } from 'react';
```

_Hook (page view):_
```jsx
useEffect(() => { track('pageView', { __pv: true, pageName: 'PageView_EnterNumber', eVar30: 'PageView_EnterNumber' }); }, []);
```
### KPI: [EnterNumber] Utilization of 'Back' button
- **Action**: `back`
- **Adobe**: var=`eVar31`, value=`Back_EnterNumber`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/EnterNumber.js:10`  (confidence 0.87)
- **Why here**: The Back button is located in the EnterNumber component, making it the appropriate place to track this action.
- **Event**: `Back Button Clicked`
- **Params:**
```json
{
  "eVar31": "Back_EnterNumber",
  "events": "event1",
  "__pv": false,
  "pageName": "EnterNumber"
}
```
- **Implementation**: Track the click event on the Back button to capture user navigation behavior.
- **Risks**: Event may not fire if button is not clicked, User may navigate away before tracking occurs

```jsx
   4: export default function EnterNumber(){
   5:   const nav=useNavigate(); const {state}=useLocation(); const billType=state?.billType||'Mobile';
   6:   const [value,setValue]=useState(''); const maxLen=billType==='Mobile'?10:12;
   7:   const onKey=(k)=>{ if(k==='Clear') return setValue(''); if(k==='⌫') return setValue(v=>v.slice(0,-1)); if(/^\d$/.test(k)) setValue(v=>(v+k).slice(0,maxLen)); };
   8:   const onSubmit=(e)=>{ e.preventDefault(); if(value.length<Math.min(6,maxLen)) return; alert(`Mock submit for ${billType}: ${value}`); };
   9:   return(<div className="screen"><div className="page">
  10:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
  11:     <h1 className="hero">Enter your {billType.toLowerCase()} number or account number.</h1>
  12:     <form className="entry" onSubmit={onSubmit}>
  13:       <label className="field"><span className="label">{billType} number or account number</span>
  14:         <input type="text" inputMode="numeric" pattern="\d*" value={value} onChange={(e)=>setValue(e.target.value.replace(/\D/g,'').slice(0,maxLen))}/>
  15:       </label>
  16:       <Keypad onPress={onKey}/>
```

**Suggested code to add:**

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('Back Button Clicked', { eVar31: 'Back_EnterNumber', events: 'event1' }); nav(-1); }}
>
  ...
</YourElement>
```
### KPI: [EnterNumber] Utilization of 'Exit' link
- **Action**: `exit`
- **Adobe**: var=`eVar32`, value=`Exit_EnterNumber`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/EnterNumber.js:10`  (confidence 0.87)
- **Why here**: The exit link is located in the EnterNumber component, making it the appropriate place to track the exit action.
- **Event**: `exit_link_click`
- **Params:**
```json
{
  "eVar32": "Exit_EnterNumber",
  "events": "event1",
  "__pv": false,
  "pageName": "EnterNumber"
}
```
- **Implementation**: Track the exit link click to measure user engagement with the exit functionality.
- **Risks**: User may not click the exit link, Tracking may not capture all exit scenarios

```jsx
   4: export default function EnterNumber(){
   5:   const nav=useNavigate(); const {state}=useLocation(); const billType=state?.billType||'Mobile';
   6:   const [value,setValue]=useState(''); const maxLen=billType==='Mobile'?10:12;
   7:   const onKey=(k)=>{ if(k==='Clear') return setValue(''); if(k==='⌫') return setValue(v=>v.slice(0,-1)); if(/^\d$/.test(k)) setValue(v=>(v+k).slice(0,maxLen)); };
   8:   const onSubmit=(e)=>{ e.preventDefault(); if(value.length<Math.min(6,maxLen)) return; alert(`Mock submit for ${billType}: ${value}`); };
   9:   return(<div className="screen"><div className="page">
  10:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
  11:     <h1 className="hero">Enter your {billType.toLowerCase()} number or account number.</h1>
  12:     <form className="entry" onSubmit={onSubmit}>
  13:       <label className="field"><span className="label">{billType} number or account number</span>
  14:         <input type="text" inputMode="numeric" pattern="\d*" value={value} onChange={(e)=>setValue(e.target.value.replace(/\D/g,'').slice(0,maxLen))}/>
  15:       </label>
  16:       <Keypad onPress={onKey}/>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from "../analytics/track.js";
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
data-analytics-id="exit_enternumber"
onClick={(e) => {
  track("exit_link_click", {
  "eVar32": "Exit_EnterNumber",
  "events": "event1",
  "__pv": false,
  "pageName": "EnterNumber"
});
  /* originalOnClick?.(e); */
}}
>
  ...
</YourElement>
```

_Alternative wrapper (if preserving existing handler):_
```js
/* If the element uses a named handler like onClick={handleClick}, wrap it: */
const _origHandleClick = typeof handleClick === 'function' ? handleClick : null;
const handleClickTracked = (e) => {
  track("exit_link_click", {
  "eVar32": "Exit_EnterNumber",
  "events": "event1",
  "__pv": false,
  "pageName": "EnterNumber"
});
  if (_origHandleClick) return _origHandleClick(e);
};
/* then use: onClick={handleClickTracked} */
```
## Page: Help
### KPI: [Help] Page view recorded when Help page loads
- **Action**: `view`
- **Adobe**: var=`eVar20`, value=`PageView_Help`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:7`  (confidence 0.85)
- **Why here**: The Help page view is relevant to the BillType component as it includes navigation to the Help page.
- **Event**: `pageView`
- **Params:**
```json
{
  "__pv": true,
  "pageName": "Help",
  "eVar20": "PageView_Help"
}
```
- **Implementation**: Add a useEffect hook to track the page view when the component mounts.
- **Risks**: Potential for duplicate tracking if not managed correctly, User may navigate away before tracking occurs

```jsx
   1: import React from 'react';
   2: import { useNavigate } from 'react-router-dom';
   3: export default function BillType(){
   4:   const nav=useNavigate();
   5:   const pick=(type)=>nav('/enter-number',{state:{billType:type}});
   6:   return(<div className="screen"><div className="page">
   7:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
   8:     <h1 className="hero">What type of bill do you want to pay?</h1>
   9:     <div className="grid-2 compact">
  10:       <div className="tile big" onClick={()=>pick('Mobile')}><span>Mobile</span></div>
  11:       <div className="tile big" onClick={()=>pick('Home Internet')}><span>Home Internet</span></div>
  12:     </div></div></div>);
  13: }
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { useEffect } from 'react';
```

_Hook (page view):_
```jsx
useEffect(() => { track('pageView', { __pv: true, pageName: 'Help', eVar20: 'PageView_Help' }); }, []);
```
### KPI: [Help] Utilization of 'Español' link
- **Action**: `nav`
- **Adobe**: var=`eVar22`, value=`Nav_Espanol`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/Help.js:6`  (confidence 0.85)
- **Why here**: The link for 'Español' is present in the Help page, making it the appropriate location for tracking navigation.
- **Event**: `nav`
- **Params:**
```json
{
  "eVar22": "Nav_Espanol",
  "__pv": true,
  "pageName": "Help"
}
```
- **Implementation**: Track the click event on the 'Español' link to capture navigation.
- **Risks**: Link may not be clicked frequently, Potential for missing tracking if not implemented correctly

```jsx
   1: import React from 'react';
   2: import { useNavigate } from 'react-router-dom';
   3: export default function Help(){
   4:   const nav=useNavigate();
   5:   return(<div className="screen"><div className="page">
   6:     <div className="toolbar"><div className="pill">Today ▾</div><div className="spacer"/><a className="link ghost" href="#">Español</a><a className="link ghost" href="#">Reviews</a></div>
   7:     <h1 className="hero red">How can we help you today?</h1>
   8:     <div className="grid-2">
   9:       <div className="card action" onClick={()=>nav('/bill-type')}><h3>Pay your bill</h3><p>Make a one-time payment toward your mobile or home internet bill.</p><div className="chev">→</div></div>
  10:       <div className="card"><h3>Complete your order</h3><p>Access your order to proceed with payment.</p><div className="chev">→</div></div>
  11:       <div className="card"><h3>Scan &amp; Go</h3><p>Scan the barcode to complete your accessory purchase.</p><div className="chev">→</div></div>
  12:       <div className="card ghost"><h3>More options</h3><p>Coming soon.</p></div>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import React from 'react';
import { useNavigate } from 'react-router-dom';
```

_Hook (page view):_
```jsx
useEffect(() => { track('nav', { __pv: true, pageName: 'Help' }); }, []);
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => track('nav', { eVar22: 'Nav_Espanol', __pv: true, pageName: 'Help' })}
>
  ...
</YourElement>
```

_Alternative wrapper (if preserving existing handler):_
```js
onClick={handleClick}
```
### KPI: [Help] Utilization of 'Pay your bill' button
- **Action**: `click`
- **Adobe**: var=`eVar21`, value=`CTA_PayYourBill`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/Help.js:9`  (confidence 0.85)
- **Why here**: The event handler for the 'Pay your bill' button is located in the Help.js file, making it the appropriate place to implement the tracking.
- **Event**: `PayYourBill_Click`
- **Params:**
```json
{
  "eVar21": "CTA_PayYourBill",
  "pageName": "Help"
}
```
- **Implementation**: Track the click event on the 'Pay your bill' button to capture user interaction.
- **Risks**: Event tracking may not fire if the button is not clicked., Potential for duplicate events if the click handler is not properly managed.

```jsx
   3: export default function Help(){
   4:   const nav=useNavigate();
   5:   return(<div className="screen"><div className="page">
   6:     <div className="toolbar"><div className="pill">Today ▾</div><div className="spacer"/><a className="link ghost" href="#">Español</a><a className="link ghost" href="#">Reviews</a></div>
   7:     <h1 className="hero red">How can we help you today?</h1>
   8:     <div className="grid-2">
   9:       <div className="card action" onClick={()=>nav('/bill-type')}><h3>Pay your bill</h3><p>Make a one-time payment toward your mobile or home internet bill.</p><div className="chev">→</div></div>
  10:       <div className="card"><h3>Complete your order</h3><p>Access your order to proceed with payment.</p><div className="chev">→</div></div>
  11:       <div className="card"><h3>Scan &amp; Go</h3><p>Scan the barcode to complete your accessory purchase.</p><div className="chev">→</div></div>
  12:       <div className="card ghost"><h3>More options</h3><p>Coming soon.</p></div>
  13:     </div></div></div>);
  14: }
```

**Suggested code to add:**

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('PayYourBill_Click', { eVar21: 'CTA_PayYourBill' }); nav('/bill-type'); }}
>
  ...
</YourElement>
```
### KPI: [Help] Utilization of 'Reviews' link
- **Action**: `nav`
- **Adobe**: var=`eVar23`, value=`Nav_Reviews`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/Help.js:6`  (confidence 0.85)
- **Why here**: The code contains a clickable JSX element for the 'Reviews' link, making it suitable for tracking navigation events.
- **Event**: `nav`
- **Params:**
```json
{
  "eVar23": "Nav_Reviews",
  "pageName": "Help"
}
```
- **Implementation**: Track the click event on the 'Reviews' link to capture navigation data.
- **Risks**: Link may not be clickable if not properly rendered, Potential for missing tracking if event handler is not attached

```jsx
   1: import React from 'react';
   2: import { useNavigate } from 'react-router-dom';
   3: export default function Help(){
   4:   const nav=useNavigate();
   5:   return(<div className="screen"><div className="page">
   6:     <div className="toolbar"><div className="pill">Today ▾</div><div className="spacer"/><a className="link ghost" href="#">Español</a><a className="link ghost" href="#">Reviews</a></div>
   7:     <h1 className="hero red">How can we help you today?</h1>
   8:     <div className="grid-2">
   9:       <div className="card action" onClick={()=>nav('/bill-type')}><h3>Pay your bill</h3><p>Make a one-time payment toward your mobile or home internet bill.</p><div className="chev">→</div></div>
  10:       <div className="card"><h3>Complete your order</h3><p>Access your order to proceed with payment.</p><div className="chev">→</div></div>
  11:       <div className="card"><h3>Scan &amp; Go</h3><p>Scan the barcode to complete your accessory purchase.</p><div className="chev">→</div></div>
  12:       <div className="card ghost"><h3>More options</h3><p>Coming soon.</p></div>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from '../analytics';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('nav', { eVar23: 'Nav_Reviews' }); nav('/reviews'); }}
>
  ...
</YourElement>
```

---

## Optional analytics helper
_Create `src/analytics/track.js` if you don't already have a tracking util:_
```js
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
```