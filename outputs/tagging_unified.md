# Tagging Suggestions Report

- **Excel**: `/mnt/c/Users/sgadal/AppSelector/agentic_tagging_system/techSpecAgent/TechSpecOutputs/techspec.xlsx`
- **Repo**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js`
- **Items**: 10

## Page: Bill Type Selection
### KPI: User selects a bill type (Mobile vs Home Internet) on the kiosk.
- **Action**: `select`
- **Adobe**: var=`eVar27`, value=`Select_Bill_Mobile`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:14`  (confidence 0.85)
- **Why here**: The code is located in the event handler for the clickable element representing the bill type selection.
- **Event**: `select_bill_type`
- **Params:**
```json
{
  "eVar27": "Select_Bill_Mobile",
  "events": "event1",
  "__pv": false,
  "pageName": "BillType"
}
```
- **Implementation**: Ensure to update the eVar value based on the selected bill type.
- **Risks**: Incorrect eVar value if not updated properly, Potential for duplicate events if user clicks multiple times

```jsx
   8:   return(<div className="screen"><div className="page">
   9:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
  10:     <h1 className="hero">What type of bill do you want to pay?</h1>
  11:     <div className="grid-2 compact">
  12:       <div className="tile big" onClick={(e) => {
  13:         track("select_bill_type", {
  14:           "eVar11": "Select_BillType_Mobile",
  15:           "events": "event1",
  16:           "__pv": false,
  17:           "pageName": "BillType"
  18:         });
  19:         pick('Mobile');
  20:       }}><span>Mobile</span></div>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from "../analytics/track.js";
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
data-analytics-id="select_bill_mobile"
onClick={(e) => {
  track("select_bill_type", {
  "eVar27": "Select_Bill_Mobile",
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
  "eVar27": "Select_Bill_Mobile",
  "events": "event1",
  "__pv": false,
  "pageName": "BillType"
});
  if (_origHandleClick) return _origHandleClick(e);
};
/* then use: onClick={handleClickTracked} */
```
### KPI: User selects a bill type (Mobile vs Home Internet) on the kiosk.
- **Action**: `select`
- **Adobe**: var=`eVar27`, value=`Select_Bill_HomeInternet`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:14`  (confidence 0.85)
- **Why here**: The code is located in the event handler for the clickable element representing the bill type selection.
- **Event**: `select_bill_type`
- **Params:**
```json
{
  "eVar27": "Select_Bill_HomeInternet",
  "events": "event1",
  "__pv": false,
  "pageName": "BillType"
}
```
- **Implementation**: Update the onClick handler for the Home Internet option to track the selection correctly.
- **Risks**: Incorrect event tracking if not updated, Potential for missing data if page view flag is not set

```jsx
   8:   return(<div className="screen"><div className="page">
   9:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
  10:     <h1 className="hero">What type of bill do you want to pay?</h1>
  11:     <div className="grid-2 compact">
  12:       <div className="tile big" onClick={(e) => {
  13:         track("select_bill_type", {
  14:           "eVar11": "Select_BillType_Mobile",
  15:           "events": "event1",
  16:           "__pv": false,
  17:           "pageName": "BillType"
  18:         });
  19:         pick('Mobile');
  20:       }}><span>Mobile</span></div>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from "../analytics/track.js";
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
data-analytics-id="select_bill_homeinternet"
onClick={(e) => {
  track("select_bill_type", {
  "eVar27": "Select_Bill_HomeInternet",
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
  "eVar27": "Select_Bill_HomeInternet",
  "events": "event1",
  "__pv": false,
  "pageName": "BillType"
});
  if (_origHandleClick) return _origHandleClick(e);
};
/* then use: onClick={handleClickTracked} */
```
## Page: Billing Process
### KPI: Session Abandonment
- **Action**: `exit`
- **Adobe**: var=`eVar27`, value=`SessionAbandonment`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The Keypad component contains user interaction elements that could lead to session abandonment.
- **Event**: `sessionAbandonment`
- **Params:**
```json
{
  "eVar27": "SessionAbandonment",
  "pageName": "Billing Process"
}
```
- **Implementation**: Track when the user abandons the session during the billing process.
- **Risks**: User may not abandon session at this point, Tracking may not capture all abandonment scenarios

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
import { useEffect } from 'react';
```

_Hook (page view):_
```jsx
useEffect(() => { return () => { track('sessionAbandonment', { eVar27: 'SessionAbandonment' }); }; }, []);
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('sessionAbandonment', { eVar27: 'SessionAbandonment' }); onPress && onPress(k); }}
>
  ...
</YourElement>
```
### KPI: User interacts with the keypad during the billing process.
- **Action**: `select`
- **Adobe**: var=`eVar27`, value=`KeypadInteraction`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The Keypad component contains the event handler for user interactions.
- **Event**: `Keypad Interaction`
- **Params:**
```json
{
  "eVar27": "KeypadInteraction",
  "pageName": "Billing Process"
}
```
- **Implementation**: Track the interaction when a key is pressed.
- **Risks**: Event may not fire if onPress is not defined, Potential performance impact if too many events are tracked

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
import { track } from '../analytics';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('Keypad Interaction', { eVar27: 'KeypadInteraction' }); onPress && onPress(k); }}
>
  ...
</YourElement>
```
### KPI: User navigates through the billing process pages.
- **Action**: `nav`
- **Adobe**: var=`eVar27`, value=`PageNavigation`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:12`  (confidence 0.87)
- **Why here**: The code is located in the BillType.js file where user navigation occurs.
- **Event**: `pageNavigation`
- **Params:**
```json
{
  "__pv": true,
  "pageName": "PageNavigation",
  "eVar27": "PageNavigation"
}
```
- **Implementation**: Add tracking for page navigation in the billing process.
- **Risks**: Potential for duplicate tracking if not managed correctly, Incorrect pageName may lead to misattributed data

```jsx
   6:   const pick=(type)=>nav('/enter-number',{state:{billType:type}});
   7:   useEffect(() => { track('pageView', { __pv: true, pageName: 'PageView_BillType', eVar10: 'PageView_BillType' }); }, []);
   8:   return(<div className="screen"><div className="page">
   9:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
  10:     <h1 className="hero">What type of bill do you want to pay?</h1>
  11:     <div className="grid-2 compact">
  12:       <div className="tile big" onClick={(e) => {
  13:         track("select_bill_type", {
  14:           "eVar11": "Select_BillType_Mobile",
  15:           "events": "event1",
  16:           "__pv": false,
  17:           "pageName": "BillType"
  18:         });
```

**Suggested code to add:**

_Hook (page view):_
```jsx
useEffect(() => { track('pageNavigation', { __pv: true, pageName: 'PageNavigation', eVar27: 'PageNavigation' }); }, []);
```
## Page: Data Entry
### KPI: User encounters an input validation error during data entry.
- **Action**: `view`
- **Adobe**: var=`eVar27`, value=`InputValidationError`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The Keypad component handles user input, making it relevant for tracking input validation errors.
- **Event**: `Input Validation Error`
- **Params:**
```json
{
  "eVar27": "InputValidationError",
  "__pv": true,
  "pageName": "Data Entry"
}
```
- **Implementation**: Track the event when an input validation error occurs during data entry.
- **Risks**: Event may not trigger if validation logic is not implemented, Potential performance impact if tracking is not optimized

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
import { useEffect } from 'react';
```

_Hook (page view):_
```jsx
useEffect(() => { track('Input Validation Error', { eVar27: 'InputValidationError', __pv: true, pageName: 'Data Entry' }); }, []);
```
## Page: Input Validation
### KPI: User takes recovery action after an input validation error
- **Action**: `submit`
- **Adobe**: var=`eVar27`, value=`InputRecoveryAction`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The event handler for button clicks is located in the Keypad component, which is where user input is processed.
- **Event**: `InputRecoveryAction`
- **Params:**
```json
{
  "eVar27": "InputRecoveryAction",
  "pageName": "Input Validation"
}
```
- **Implementation**: Track the recovery action when the user submits corrected input.
- **Risks**: Event may not trigger if onPress is not defined, Potential for multiple submissions if not handled correctly

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
import { track } from '../analytics';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { onPress && onPress(k); track('InputRecoveryAction', { eVar27: 'InputRecoveryAction' }); }}
>
  ...
</YourElement>
```
## Page: Kiosk
### KPI: User engages with the kiosk (interacts with buttons, navigates through screens).
- **Action**: `nav`
- **Adobe**: var=`eVar27`, value=`UserEngagement`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:2`  (confidence 0.85)
- **Why here**: The file contains a clickable JSX element and an event handler related to navigation.
- **Event**: `userEngagement`
- **Params:**
```json
{
  "eVar27": "UserEngagement",
  "__pv": true,
  "pageName": "PageView_BillType"
}
```
- **Implementation**: Ensure that the track function is called on user interactions with buttons.
- **Risks**: Potential for missing events if not all interactions are tracked, Overlapping events may cause confusion in analytics

```jsx
   1: import React, { useEffect } from 'react';
   2: import { useNavigate } from 'react-router-dom';
   3: import { track } from '../analytics/track.js';
   4: export default function BillType(){
   5:   const nav=useNavigate();
   6:   const pick=(type)=>nav('/enter-number',{state:{billType:type}});
   7:   useEffect(() => { track('pageView', { __pv: true, pageName: 'PageView_BillType', eVar10: 'PageView_BillType' }); }, []);
   8:   return(<div className="screen"><div className="page">
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from '../analytics/track.js';
```

_Hook (page view):_
```jsx
useEffect(() => { track('pageView', { __pv: true, pageName: 'PageView_BillType', eVar10: 'PageView_BillType' }); }, []);
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('userEngagement', { eVar27: 'UserEngagement' }); pick('someType'); }}
>
  ...
</YourElement>
```
## Page: Kiosk Session
### KPI: User initiates a session on the kiosk.
- **Action**: `view`
- **Adobe**: var=`eVar27`, value=`SessionInitiation`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The Keypad component handles user interactions, making it suitable for tracking session initiation.
- **Event**: `kioskSessionInitiation`
- **Params:**
```json
{
  "eVar27": "SessionInitiation",
  "__pv": true,
  "pageName": "Kiosk Session"
}
```
- **Implementation**: Track the session initiation when the user interacts with the keypad.
- **Risks**: Event may not trigger if onPress is not called, Potential for duplicate tracking if multiple buttons are pressed

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
import { useEffect } from 'react';
```

_Hook (page view):_
```jsx
useEffect(() => { track('kioskSessionInitiation', { eVar27: 'SessionInitiation', __pv: true, pageName: 'Kiosk Session' }); }, []);
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { onPress && onPress(k); track('kioskSessionInitiation', { eVar27: 'SessionInitiation', __pv: true, pageName: 'Kiosk Session' }); }}
>
  ...
</YourElement>
```
## Page: Phone Entry
### KPI: User completes the entry of a phone or account number.
- **Action**: `submit`
- **Adobe**: var=`eVar27`, value=`PhoneNumberEntryCompletion`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/EnterNumber.js:29`  (confidence 0.86)
- **Why here**: The form submission is handled in the EnterNumber.js file, making it the appropriate location for tracking the completion of the phone or account number entry.
- **Event**: `PhoneNumberEntryCompletion`
- **Params:**
```json
{
  "eVar27": "PhoneNumberEntryCompletion",
  "events": "event1",
  "__pv": false,
  "pageName": "EnterNumber"
}
```
- **Implementation**: Track the form submission event to capture when the user completes entering their phone or account number.
- **Risks**: Event may not fire if form validation fails, User may navigate away before submission

```jsx
  23:   "events": "event1",
  24:   "__pv": false,
  25:   "pageName": "EnterNumber"
  26: });
  27:   nav('/help');
  28: }}>Exit</button></div>
  29:     <h1 className="hero">Enter your {billType.toLowerCase()} number or account number.</h1>
  30:     <form className="entry" onSubmit={onSubmit}>
  31:       <label className="field"><span className="label">{billType} number or account number</span>
  32:         <input type="text" inputMode="numeric" pattern="\d*" value={value} onChange={(e)=>setValue(e.target.value.replace(/\D/g,'').slice(0,maxLen))}/>
  33:       </label>
  34:       <Keypad onPress={onKey}/>
  35:       <button type="submit" className="btn primary" disabled={value.length<Math.min(6,maxLen)}>Continue</button>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from "../analytics/track.js";
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
data-analytics-id="phonenumberentrycompletion"
onClick={(e) => {
  track("PhoneNumberEntryCompletion", {
  "eVar27": "PhoneNumberEntryCompletion",
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
  track("PhoneNumberEntryCompletion", {
  "eVar27": "PhoneNumberEntryCompletion",
  "events": "event1",
  "__pv": false,
  "pageName": "EnterNumber"
});
  if (_origHandleClick) return _origHandleClick(e);
};
/* then use: onClick={handleClickTracked} */
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