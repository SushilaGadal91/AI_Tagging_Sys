# Tagging Suggestions Report

- **Excel**: `/mnt/c/Users/sgadal/AppSelector/agentic_tagging_system/core/techSpecAgent/TechSpecOutputs/techspec.xlsx`
- **Repo**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js`
- **Items**: 6

## Page: Account Entry
### KPI: Continue_AccountEntry_Mobile
- **Action**: `click`
- **Adobe**: var=`eVar27`, value=`Continue_AccountEntry_Mobile`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/EnterNumber.js:17`  (confidence 0.85)
- **Why here**: The button for CONTINUE is located in the EnterNumber.js file, which handles the account entry process.
- **Event**: `click`
- **Params:**
```json
{
  "eVar27": "Continue_AccountEntry_Mobile",
  "pageName": "Account Entry"
}
```
- **Implementation**: Track the click event when the CONTINUE button is pressed.
- **Risks**: Button may not be clickable if disabled, User may not enter a valid mobile number

```jsx
  11:     <h1 className="hero">Enter your {billType.toLowerCase()} number or account number.</h1>
  12:     <form className="entry" onSubmit={onSubmit}>
  13:       <label className="field"><span className="label">{billType} number or account number</span>
  14:         <input type="text" inputMode="numeric" pattern="\d*" value={value} onChange={(e)=>setValue(e.target.value.replace(/\D/g,'').slice(0,maxLen))}/>
  15:       </label>
  16:       <Keypad onPress={onKey}/>
  17:       <button type="submit" className="btn primary" disabled={value.length<Math.min(6,maxLen)}>Continue</button>
  18:     </form></div></div>);
  19: }
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from '../analytics/track.js';
```

_Hook (page view):_
```jsx
useEffect(() => { return () => { /* cleanup if necessary */ }; }, []);
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => track('click', { eVar27: 'Continue_AccountEntry_Mobile' })}
>
  ...
</YourElement>
```

_Alternative wrapper (if preserving existing handler):_
```js
onClick={handleClick}
```
## Page: Billing
### KPI: When the customer selects 'Pay Bill'
- **Action**: `select`
- **Adobe**: var=`eVar27`, value=`Select_PayBill`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The event handler for button clicks is located in Keypad.js, making it suitable for tracking the selection of 'Pay Bill'.
- **Event**: `selectPayBill`
- **Params:**
```json
{
  "eVar27": "Select_PayBill",
  "events": "event1",
  "pageName": "Billing"
}
```
- **Implementation**: Ensure that the onPress function is modified to include the tracking call.
- **Risks**: Incorrect event tracking if onPress is not modified, Potential performance impact if tracking is not optimized

```jsx
   1: import React from 'react';
   2: export default function Keypad({ onPress }){
   3:   const keys=['1','2','3','4','5','6','7','8','9','Clear','0','⌫'];
   4:   return (<div className="keypad">{keys.map(k=>(<button key={k} className="key" onClick={()=>onPress&&onPress(k)}>{k}</button>))}</div>);
   5: }
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from '../analytics/track.js';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('selectPayBill', { eVar27: 'Select_PayBill', events: 'event1' }); onPress && onPress(k); }}
>
  ...
</YourElement>
```
## Page: Billing Options
### KPI: When the customer selects Home Internet
- **Action**: `select`
- **Adobe**: var=`eVar27`, value=`Select_BillType_HomeInternet`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:11`  (confidence 0.85)
- **Why here**: The event handler for selecting Home Internet is located on line 11 of BillType.js.
- **Event**: `selectBillType`
- **Params:**
```json
{
  "eVar27": "Select_BillType_HomeInternet",
  "pageName": "Billing Options"
}
```
- **Implementation**: Track the selection of Home Internet as a user action.
- **Risks**: Event may not fire if the onClick is not properly set up., Potential for duplicate events if not managed correctly.

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
import { track } from '../analytics/track.js';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('selectBillType', { eVar27: 'Select_BillType_HomeInternet' }); pick('Home Internet'); }}
>
  ...
</YourElement>
```
## Page: Billing Type Selection
### KPI: When the customer selects Mobile
- **Action**: `select`
- **Adobe**: var=`eVar27`, value=`Select_BillType_Mobile`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:10`  (confidence 0.85)
- **Why here**: The event handler for the Mobile selection is located in the BillType.js file.
- **Event**: `select_bill_type`
- **Params:**
```json
{
  "eVar27": "Select_BillType_Mobile",
  "events": "event1",
  "__pv": false,
  "pageName": "Billing Type Selection"
}
```
- **Implementation**: Track the selection of the Mobile billing type.
- **Risks**: Incorrect event tracking if not implemented properly, Potential performance impact if tracking is not optimized

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
import { track } from '../analytics/track.js';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('select_bill_type', { eVar27: 'Select_BillType_Mobile' }); pick('Mobile'); }}
>
  ...
</YourElement>
```
## Page: Home Internet
### KPI: Continue_AccountEntry_HomeInternet
- **Action**: `submit`
- **Adobe**: var=`eVar27`, value=`Continue_AccountEntry_HomeInternet`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/EnterNumber.js:17`  (confidence 0.85)
- **Why here**: The submit button for the account entry form is where the user interaction occurs.
- **Event**: `event1`
- **Params:**
```json
{
  "eVar27": "Continue_AccountEntry_HomeInternet",
  "__pv": false,
  "pageName": "Home Internet"
}
```
- **Implementation**: Track the event when the user submits the form with a valid account number.
- **Risks**: User may not enter a valid account number, Form submission may fail due to network issues

```jsx
  11:     <h1 className="hero">Enter your {billType.toLowerCase()} number or account number.</h1>
  12:     <form className="entry" onSubmit={onSubmit}>
  13:       <label className="field"><span className="label">{billType} number or account number</span>
  14:         <input type="text" inputMode="numeric" pattern="\d*" value={value} onChange={(e)=>setValue(e.target.value.replace(/\D/g,'').slice(0,maxLen))}/>
  15:       </label>
  16:       <Keypad onPress={onKey}/>
  17:       <button type="submit" className="btn primary" disabled={value.length<Math.min(6,maxLen)}>Continue</button>
  18:     </form></div></div>);
  19: }
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from '../analytics/track.js';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => track('event1', { eVar27: 'Continue_AccountEntry_HomeInternet' })}
>
  ...
</YourElement>
```

_Alternative wrapper (if preserving existing handler):_
```js
onSubmit={(e) => { e.preventDefault(); track('event1', { eVar27: 'Continue_AccountEntry_HomeInternet' }); onSubmit(e); }}
```
## Page: unknown
### KPI: When the customer taps the BACK button
- **Action**: `back`
- **Adobe**: var=`eVar27`, value=`Back`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:7`  (confidence 0.85)
- **Why here**: The BACK button is a clickable JSX element that triggers navigation.
- **Event**: `back_button_click`
- **Params:**
```json
{
  "eVar27": "Back",
  "events": "event1",
  "__pv": false,
  "pageName": "unknown"
}
```
- **Implementation**: Track the BACK button click event to capture user navigation behavior.
- **Risks**: User may not expect tracking on BACK button, Potential performance impact if tracking is not optimized

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
import { track } from '../analytics/track.js';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('back_button_click', { eVar27: 'Back' }); nav(-1); }}
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