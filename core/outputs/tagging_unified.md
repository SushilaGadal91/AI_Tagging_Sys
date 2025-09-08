# Tagging Suggestions Report

- **Excel**: `/mnt/c/Users/sgadal/AppSelector/agentic_tagging_system/core/techSpecAgent/TechSpecOutputs/techspec.xlsx`
- **Repo**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js`
- **Items**: 9

## Page: Bill Type Selection
### KPI: User selects a bill type (Mobile vs Home Internet) on the kiosk.
- **Action**: `select`
- **Adobe**: var=`eVar27`, value=`BillTypeSelection`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/BillType.js:11`  (confidence 0.86)
- **Why here**: The event handler for the bill type selection is located in the BillType.js file.
- **Event**: `BillTypeSelection`
- **Params:**
```json
{
  "eVar27": "BillTypeSelection",
  "pageName": "Bill Type Selection"
}
```
- **Implementation**: Track the selection of bill types when the user clicks on either option.
- **Risks**: Incorrect event tracking if not implemented properly, Potential performance issues if tracking is not optimized

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
onClick={() => { track('BillTypeSelection', { eVar27: 'Mobile' }); pick('Mobile'); }}
>
  ...
</YourElement>
```

_Alternative wrapper (if preserving existing handler):_
```js
onClick={() => { track('BillTypeSelection', { eVar27: 'Home Internet' }); pick('Home Internet'); }}
```
## Page: Billing Process
### KPI: User abandons the session at any stage of the billing process.
- **Action**: `exit`
- **Adobe**: var=`eVar27`, value=`SessionAbandonment`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The Keypad component contains clickable elements that may lead to session abandonment.
- **Event**: `SessionAbandonment`
- **Params:**
```json
{
  "eVar27": "SessionAbandonment",
  "pageName": "Billing Process"
}
```
- **Implementation**: Track abandonment when the user interacts with the keypad.
- **Risks**: User may not abandon session on every interaction, Tracking may not capture all abandonment scenarios

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
onClick={() => { track('SessionAbandonment', { eVar27: 'SessionAbandonment' }); onPress && onPress(k); }}
>
  ...
</YourElement>
```
### KPI: User interacts with the keypad during the billing process.
- **Action**: `select`
- **Adobe**: var=`eVar27`, value=`KeypadInteraction`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The Keypad component contains the event handler for user interactions.
- **Event**: `KeypadInteraction`
- **Params:**
```json
{
  "eVar27": "KeypadInteraction",
  "pageName": "Billing Process"
}
```
- **Implementation**: Track interactions when a key is pressed.
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
import { track } from '../analytics/track.js';
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('KeypadInteraction', { eVar27: 'KeypadInteraction' }); onPress && onPress(k); }}
>
  ...
</YourElement>
```
### KPI: User navigates through the billing process pages.
- **Action**: `nav`
- **Adobe**: var=`eVar27`, value=`PageNavigation`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The Keypad component contains clickable elements that can trigger navigation events.
- **Event**: `PageNavigation`
- **Params:**
```json
{
  "eVar27": "PageNavigation",
  "__pv": true,
  "pageName": "Billing Process"
}
```
- **Implementation**: Track navigation events when users interact with the keypad.
- **Risks**: Event may not fire if onPress is not defined, Potential for duplicate events if not managed correctly

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
onClick={() => { track('PageNavigation', { eVar27: 'PageNavigation', __pv: true, pageName: 'Billing Process' }); onPress && onPress(k); }}
>
  ...
</YourElement>
```
## Page: Data Entry
### KPI: User encounters an input validation error during data entry.
- **Action**: `general`
- **Adobe**: var=`eVar27`, value=`InputValidationError`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The event handler for button clicks is located in the Keypad component, making it suitable for tracking input validation errors.
- **Event**: `Input Validation Error`
- **Params:**
```json
{
  "eVar27": "InputValidationError",
  "pageName": "Data Entry"
}
```
- **Implementation**: Track the event when an input validation error occurs during data entry.
- **Risks**: Event may not trigger if validation logic is not implemented, User may not encounter validation errors frequently

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
onClick={() => { onPress && onPress(k); track('Input Validation Error', { eVar27: 'InputValidationError' }); }}
>
  ...
</YourElement>
```
## Page: Input Validation
### KPI: User takes recovery action after an input validation error (e.g., corrects input).
- **Action**: `submit`
- **Adobe**: var=`eVar27`, value=`InputRecoveryAction`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The event handler for button clicks is located in the Keypad component, which is relevant for tracking user actions.
- **Event**: `InputRecoveryAction`
- **Params:**
```json
{
  "eVar27": "InputRecoveryAction",
  "pageName": "Input Validation"
}
```
- **Implementation**: Track the recovery action when a user submits corrected input.
- **Risks**: Event may not trigger if onPress is not defined, Potential for multiple rapid submissions

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
- **Why here**: The file contains event handlers for button clicks, which are relevant for tracking user interactions.
- **Event**: `kioskInteraction`
- **Params:**
```json
{
  "eVar27": "UserEngagement",
  "pageName": "Kiosk"
}
```
- **Implementation**: Track user interactions with buttons and navigation.
- **Risks**: Potential for missing interactions if not all buttons are tracked, Overhead of tracking multiple events may affect performance

```jsx
   1: import React from 'react';
   2: import { useNavigate } from 'react-router-dom';
   3: export default function BillType(){
   4:   const nav=useNavigate();
   5:   const pick=(type)=>nav('/enter-number',{state:{billType:type}});
   6:   return(<div className="screen"><div className="page">
   7:     <div className="toolbar"><button className="link" onClick={()=>nav(-1)}>← Back</button><div className="spacer"/><button className="link" onClick={()=>nav('/help')}>Exit</button></div>
   8:     <h1 className="hero">What type of bill do you want to pay?</h1>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from '../analytics/track.js';
```

_Hook (page view):_
```jsx
useEffect(() => { track('kioskInteraction', { eVar27: 'UserEngagement' }); }, []);
```

_JSX attributes (apply to the element):_
```jsx
<YourElement
onClick={() => { track('kioskInteraction', { eVar27: 'UserEngagement' }); nav('/enter-number', { state: { billType: type } }); }}
>
  ...
</YourElement>
```

_Alternative wrapper (if preserving existing handler):_
```js
onClick={altHandler => { track('kioskInteraction', { eVar27: 'UserEngagement' }); altHandler(); }}
```
## Page: Kiosk Session
### KPI: User initiates a session on the kiosk.
- **Action**: `view`
- **Adobe**: var=`eVar27`, value=`SessionInitiation`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/components/Keypad.js:2`  (confidence 0.85)
- **Why here**: The Keypad component is likely involved in user interactions that initiate a session.
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
- **Risks**: Event may not trigger if onPress is not called, Potential for multiple events if user clicks rapidly

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
onClick={() => { onPress && onPress(k); track('kioskSessionInitiation', { eVar27: 'SessionInitiation', __pv: true, pageName: 'Kiosk Session' }); }}
>
  ...
</YourElement>
```
## Page: Phone Entry
### KPI: User completes the entry of a phone or account number.
- **Action**: `submit`
- **Adobe**: var=`eVar27`, value=`PhoneNumberEntryCompletion`
- **Suggested Location**: `/mnt/c/Users/sgadal/AppSelector/react-kiosk-billing-js/src/pages/EnterNumber.js:11`  (confidence 0.85)
- **Why here**: The form submission handler is where the user completes the entry.
- **Event**: `PhoneNumberEntryCompletion`
- **Params:**
```json
{
  "eVar27": "PhoneNumberEntryCompletion",
  "events": "event1",
  "__pv": false,
  "pageName": "Phone Entry"
}
```
- **Implementation**: Track the event when the form is successfully submitted.
- **Risks**: User may not complete the form, Validation errors may prevent tracking

```jsx
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
  17:       <button type="submit" className="btn primary" disabled={value.length<Math.min(6,maxLen)}>Continue</button>
```

**Suggested code to add:**

_Imports (add once per file if missing):_
```js
import { track } from '../analytics/track.js';
```

_Alternative wrapper (if preserving existing handler):_
```js
const onSubmit=(e)=>{ e.preventDefault(); if(value.length<Math.min(6,maxLen)) return; track('PhoneNumberEntryCompletion', { eVar27: 'PhoneNumberEntryCompletion', events: 'event1' }); alert(`Mock submit for ${billType}: ${value}`); };
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