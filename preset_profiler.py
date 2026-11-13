# /// script
# [tool.orcaslicer.plugin]
# name = "Preset Profiler"
# description = "Overview of your own printer, filament and process presets: bindings, checks, changes after updates, data sheets, CSV/HTML export. Read-only. / Übersicht der eigenen Profile: Zuordnung, Prüfungen, Änderungen, Datenblätter, Export. Liest nur."
# author = "Ruben Etzkorn · rubi3dp.de"
# version = "0.9.4"
# ///
import orca, os, sys, re, json, csv, io, time, datetime, traceback

VERSION = "0.9.4"
TEMPLATE = '<!DOCTYPE html>\n<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<title>Preset Profiler</title>\n<style>\n:root{--fg:var(--orca-fg,#222);--bg:var(--orca-bg,#f6f7f7);--mu:var(--orca-muted,#666);--ac:var(--orca-accent,#0e6f78);--acf:var(--orca-accent-fg,#fff);--bd:var(--orca-border,#d9dddf);--w:#e08a3c}\n*{box-sizing:border-box}\nbody{margin:0;font:13px/1.35 var(--orca-font,Barlow,"Helvetica Neue",Arial,sans-serif);color:var(--fg);background:var(--bg)}\nheader{background:var(--bg);border-bottom:2px solid var(--ac);padding:8px 14px;position:sticky;top:0;z-index:5}\n.top{display:flex;align-items:baseline;gap:14px}.top h1{font-size:17px;margin:0;color:var(--ac);font-weight:600}\n.tabrow{display:flex;align-items:center;margin-top:8px}.tabrow .tabs{margin-top:0}.brand{margin-left:auto;padding-left:12px;color:var(--fg);line-height:0;opacity:.9}.stand{color:var(--mu);font:11px "IBM Plex Mono",Menlo,monospace}.lang{margin-left:auto}\n.lang button,.tabs button{border:1px solid var(--bd);background:transparent;color:var(--fg);padding:3px 9px;cursor:pointer;font:inherit;margin:0}\n.tabs button.hl{border-color:var(--w);color:var(--w);font-weight:600}.tabs button.hl.on{background:var(--w);color:#fff}.lang button.on,.tabs button.on{background:var(--ac);color:var(--acf);border-color:var(--ac)}\n.filters{display:flex;flex-wrap:wrap;gap:8px;margin-top:7px;align-items:center}\nselect,input[type=search]{font:inherit;padding:3px 5px;border:1px solid var(--bd);background:var(--bg);color:var(--fg)}\ninput[type=search]{width:170px}label.chk{display:flex;gap:4px;align-items:center;white-space:nowrap}\n.tabs{display:flex;gap:0;margin-top:8px}.tabs button{border-right-width:0}.tabs button:last-child{border-right-width:1px}\nmain{padding:10px 14px}table{border-collapse:collapse;background:transparent;width:100%}\nth,td{border-bottom:1px solid var(--bd);padding:4px 7px;text-align:left;white-space:nowrap;color:var(--fg)}\nth{position:sticky;top:0;background:var(--bg);box-shadow:inset 0 -2px 0 var(--ac);font-weight:600;font-size:12px;cursor:pointer}\ntd.num{font-family:"IBM Plex Mono",Menlo,monospace;font-size:12px}\ntbody tr{cursor:pointer}main tbody tr:hover{background:var(--bd)}\n.kal{display:inline-block;background:var(--ac);color:var(--acf);font-size:10px;padding:0 4px;border-radius:2px;font-weight:600}\n.stu{display:inline-block;border:1px solid var(--ac);color:var(--ac);font-size:10px;padding:0 4px;border-radius:2px;font-weight:600;margin-left:3px}\n.ck{display:inline-block;border:1px solid var(--w);color:var(--w);font:600 10px "IBM Plex Mono",Menlo,monospace;padding:0 3px;margin-right:2px;border-radius:2px}\n.multi{color:var(--w)}.multi::after{content:"²";font-size:9px}\n.mx td,.mx th{text-align:center}.mx td:first-child,.mx th:first-child{text-align:left}\n.mx .dot{color:var(--ac)}.mx .K{font-weight:700;color:var(--acf);background:var(--ac);padding:0 5px}\n.mx th.rot{font-size:11px}\n.leg{color:var(--mu);font-size:11px;margin:6px 0}\n.empty{color:var(--mu)}\n.pc{display:inline-block;border:1px solid var(--ac);color:var(--fg);font-size:11px;line-height:15px;padding:0 5px;margin:0 3px 0 0;border-radius:8px}\n.pc.sys{border-style:dashed;color:var(--mu)}.pc.k{background:var(--ac);color:var(--acf)}.pc.tot{border-color:#c0504d;color:#c0504d;text-decoration:line-through}.pc.sx{border-style:dotted;color:var(--mu);font-style:italic}.pc.all{border-color:var(--w);color:var(--w);font-style:italic}.pc.mod{font-weight:600}\n#det{position:fixed;top:0;right:0;width:min(560px,100%);height:100%;background:var(--bg);border-left:2px solid var(--ac);box-shadow:-4px 0 14px #0004;transform:translateX(105%);transition:transform .15s;z-index:10;display:flex;flex-direction:column}\n#det.open{transform:none}#det .hd{padding:10px 12px;border-bottom:1px solid var(--bd)}\n#det h2{margin:0 0 3px;font-size:15px;color:var(--ac)}#det .meta{color:var(--mu);font-size:12px}\n#det .bar{display:flex;gap:10px;margin-top:7px;align-items:center}#det .x{float:right;border:0;background:none;color:var(--fg);font-size:18px;cursor:pointer}\n#det .bd{overflow:auto;flex:1}#det td{white-space:normal;word-break:break-word}#det td:first-child{font-family:"IBM Plex Mono",Menlo,monospace;font-size:11.5px;width:46%}\n#det tr{cursor:default}#det tr.ch td{background:color-mix(in srgb,var(--w) 15%,transparent)}#det .par{color:var(--mu);font-size:11px}\n#dlg{position:fixed;inset:0;background:#0006;display:none;align-items:center;justify-content:center;z-index:20}#dlg .dbox{background:var(--bg);border:2px solid var(--ac);padding:12px 16px;min-width:320px;max-width:90%;max-height:80%;overflow:auto}#dlg input{font:inherit;padding:3px 5px;width:100%;border:1px solid var(--bd);background:var(--bg);color:var(--fg)}#dlg button,.btn{border:1px solid var(--ac);background:transparent;color:var(--fg);padding:3px 10px;cursor:pointer;font:inherit}.err{color:#c0504d}\n</style></head><body>\n<header>\n <div class="top"><h1 data-t="title"></h1><span class="stand" id="stand"></span>\n  <span class="lang"><button id="ab" class="btn" style="display:none"></button> <button id="rf" style="display:none"></button> <button id="eb" style="display:none"></button> <button data-l="de">DE</button><button data-l="en">EN</button></span></div>\n <div class="filters">\n  <select id="fP"></select><select id="fT"></select><select id="fV"></select>\n  <select id="fK"></select><select id="fQ" style="display:none"></select>\n  <label class="chk"><input type="checkbox" id="fA"><span data-t="onlyIssues"></span></label>\n  <input type="search" id="fS">\n\n </div>\n <div class="tabrow"><div class="tabs" id="tabs"></div><span class="brand" title="rubi3dp.de"><svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 30 354 110" width="80" height="24.9" role="img" aria-label="rubi3dp.de"><rect x="0" y="127" width="329" height="9" rx="4.5" fill="rgb(14, 111, 120)"/><text x="0" y="122" textLength="290" lengthAdjust="spacingAndGlyphs" style="font:600 88px \'Barlow Condensed\',\'Arial Narrow\',Arial,sans-serif;fill:currentColor">rubi3dp<tspan style="fill:rgb(14, 111, 120)">.de</tspan></text><g><rect x="326" y="34" width="6" height="16" fill="currentColor"/><rect x="315" y="48" width="28" height="4" fill="currentColor"/><rect x="315" y="55" width="28" height="4" fill="currentColor"/><rect x="315" y="62" width="28" height="4" fill="currentColor"/><rect x="315" y="69" width="28" height="4" fill="currentColor"/><rect x="315" y="76" width="28" height="4" fill="currentColor"/><rect x="326" y="78" width="6" height="14" fill="currentColor"/><rect x="312" y="92" width="34" height="22" fill="currentColor"/><path d="M323 114h12l-4 12h-4z" fill="currentColor"/></g></svg></span></div>\n</header>\n<main id="main"></main>\n<aside id="det"><div class="hd"><button class="x" id="dx">×</button><h2 id="dn"></h2><div class="meta" id="dm"></div>\n <div class="bar"><input type="search" id="dS"><label class="chk"><input type="checkbox" id="dD"><span data-t="onlyDiff"></span></label><button id="bs" class="btn" style="display:none;margin-left:auto"></button></div></div>\n <div class="bd"><table><tbody id="db"></tbody></table></div></aside>\n<div id="dlg"></div>\n<script>\nlet D=/*DATA*/;\nconst T={de:{title:"Preset Profiler",stand:"Stand",allPr:"Alle Drucker",allTy:"Alle Typen",allVe:"Alle Hersteller",all:"GK + kal",gk:"nur GK",kal:"nur kal",\nonlyIssues:"nur Auffällige",search:"Suche …",tabs:["Zuordnung","Filament","Prozess","Drucker","Änderungen"],\nname:"Name",vendor:"Hersteller",type:"Typ",for:"gilt für",nozzle:"Düse °C",bed:"Bett °C",fan:"Lüfter %",mvf:"MVF",pa:"PA",flow:"Flow",shr:"Shrink XY/Z",checks:"Prüf.",notes:"Notiz",\nlh:"Schicht",hole:"Loch-K.",cont:"Kontur-K.",ef:"Elefantenf.",model:"Modell",nd:"Düse",base:"Basis",nf:"Filam.",np:"Proz.",\noff:"aus",allP:"alle",onlyDiff:"nur Abweichungen",parent:"erbt von",own:"eigen",sys:"System",binding:"Bindung",\nleg:"● passt · K = kal-Profil · Zeile anklicken für alle Werte",legM:"² = Standard / High Flow (Maus drauf)",\nc:{B0:"Bindung leer – gilt für alle Drucker",K2:"kal an mehr als einem Drucker",V:"kein eigener Drucker","KW":"Korrekturwerte gesetzt","K?":"kal ohne Korrekturwerte",KN:"Korrekturwerte ohne kal",BD:"Kompatibilitätsbedingung gesetzt – nicht auswertbar",BT:"Bindung an gelöschten Drucker",HU:"Hotend unklar – zwei Varianten, kein „Hotend:“ in der Notiz",HW:"„Hotend:“ in der Notiz passt nicht zur Variante im Profil",KP:"zugeordneter Prozess existiert nicht",PL:"leerer Eintrag in der Zuordnung – Profil wird ausgeblendet",NB:"Name passt nicht zur Bindung (Drucker/Düse)"},\nsysPrev:"Vergleich mit Systemprofil: in der Vorschau noch nicht möglich",noParent:"kein eigenes Elternprofil",viaOwn:"direkt gebunden",viaSys:"nur über Systemnamen",viaSysOnly:"Systemdrucker – kein eigenes Druckerprofil",viaMod:"alle Düsen des Modells",dead:"Drucker gibt es nicht mehr",legP:"gestrichelt = nur über Systemnamen",inP:"Elternprofil",nf_par:"nicht gefunden",refresh:"Neu einlesen",settings:"Einstellungen",allSrc:"Alle Quellen",stuPA:"aus Start-G-Code (M900)",stuNoPA:"kein M900 im Start-G-Code",stuErr:"Bambu Studio",allSheets:"Alle Datenblätter erstellen",sheet:"Datenblatt erstellen",create:"Erzeugen",cancel:"Abbrechen",noFolder:"Bitte zuerst in den Einstellungen einen Datenblatt-Ordner festlegen (danach Orca neu starten).",checking:"Prüfe …",writing:"Schreibe …",exists1:"Datenblatt existiert schon – überschreiben?",overwrite:"Überschreiben",existsN:"%v vorhanden, %n neu.",overwriteAll:"Alle überschreiben",onlyNew:"Nur neue",written:"%n Datenblatt/-blätter geschrieben",skipped:"%n übersprungen",orphans:"Diese Blätter passen zu keinem Profil mehr (bitte selbst löschen):",seen:"Übernehmen",seenHint:"aktuelle Werte werden neue Vergleichsbasis – Liste wird geleert",since:"seit",noChanges:"Keine Änderungen seit",firstRef:"Erster Stand gespeichert – ab jetzt werden Änderungen angezeigt.",ch_new:"neu",ch_gone:"entfernt",param:"Parameter",old:"vorher",new:"jetzt",prof:"Profil"},\nen:{title:"Preset Profiler",stand:"As of",allPr:"All printers",allTy:"All types",allVe:"All vendors",all:"Base + cal",gk:"Base only",kal:"Cal only",\nonlyIssues:"Issues only",search:"Search …",tabs:["Matrix","Filament","Process","Printer","Changes"],\nname:"Name",vendor:"Vendor",type:"Type",for:"Applies to",nozzle:"Nozzle °C",bed:"Bed °C",fan:"Fan %",mvf:"MVS",pa:"PA",flow:"Flow",shr:"Shrink XY/Z",checks:"Checks",notes:"Notes",\nlh:"Layer",hole:"Hole comp.",cont:"Contour comp.",ef:"Elephant f.",model:"Model",nd:"Nozzle",base:"Base",nf:"Filam.",np:"Proc.",\noff:"off",allP:"all",onlyDiff:"Differences only",parent:"Inherits",own:"own",sys:"system",binding:"Binding",\nleg:"● fits · K = calibrated profile · click a row for all values",legM:"² = Standard / High Flow (hover)",\nc:{B0:"Empty binding – applies to all printers",K2:"Calibrated profile bound to more than one printer",V:"No own printer","KW":"Correction values set","K?":"Calibrated without correction values",KN:"Correction values without cal tag",BD:"Compatibility condition set – cannot be evaluated",BT:"Bound to deleted printer",HU:"Hotend unclear – two variants, no “Hotend:” in notes",HW:"“Hotend:” in notes does not match the profile variant",KP:"Assigned process does not exist",PL:"Empty entry in assignment – profile is hidden",NB:"Name does not match binding (printer/nozzle)"},\nsysPrev:"Comparison with system profile: not available in preview",noParent:"no own parent profile",viaOwn:"bound directly",viaSys:"via system name only",viaSysOnly:"System printer – no own printer profile",viaMod:"all nozzles of model",dead:"Printer no longer exists",legP:"dashed = via system name only",inP:"Parent",nf_par:"not found",refresh:"Reload",settings:"Settings",allSrc:"All sources",stuPA:"from start G-code (M900)",stuNoPA:"no M900 in start G-code",stuErr:"Bambu Studio",allSheets:"Create all data sheets",sheet:"Create data sheet",create:"Create",cancel:"Cancel",noFolder:"Please set a data sheet folder in the settings first (then restart Orca).",checking:"Checking …",writing:"Writing …",exists1:"Data sheet already exists – overwrite?",overwrite:"Overwrite",existsN:"%v existing, %n new.",overwriteAll:"Overwrite all",onlyNew:"New only",written:"%n data sheet(s) written",skipped:"%n skipped",orphans:"These sheets no longer match any profile (please delete yourself):",seen:"Accept",seenHint:"current values become the new baseline – list is cleared",since:"since",noChanges:"No changes since",firstRef:"First state saved – changes will be shown from now on.",ch_new:"new",ch_gone:"removed",param:"Parameter",old:"before",new:"now",prof:"Profile"}};\nlet L=D.lang||"de",tab=(D.start_tab==="changes"&&(D.aend||[]).length)?4:1,sortK=null,sortD=1;const $=id=>document.getElementById(id);\nconst t=k=>T[L][k];\nconst esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",\'"\':"&quot;"}[c]));\nlet VN=[];const vnam=r=>(r&&r.v&&r.v.filament_extruder_variant||r&&r.v&&r.v.printer_extruder_variant||"").split(/";"|,/).map(x=>x.replace(/"/g,"").replace(/^Direct Drive /,"").replace(/^Bowden /,"Bowden ").trim()).filter(Boolean);\nconst mtit=s=>{const w=s.split(",");return w.map((x,i)=>(VN[i]||(i+1)+".")+" "+x).join(" · ")};\nconst val=s=>{s=s??"";if(s==="nil"||s==="")return\'<span class="empty">–</span>\';return /\\d,\\d/.test(s)?`<span class="multi" title="${esc(mtit(s))}">${esc(s.split(",")[0])}</span>`:esc(s)};\nconst pair=(a,b)=>{if((a??"")===(b??""))return val(a);return val(a)+"/"+val(b)};\nconst g=(r,k)=>String(r.v[k]??"");\nconst pct=s=>(s||"").replace(/%/g,"");\nconst nm=r=>esc(r.label||r.name)+(r.kal?\' <span class="kal">kal</span>\':"")+(r.src==="studio"?\' <span class="stu">Studio</span>\':"");\nconst ck=r=>r.checks.map(c=>`<span class="ck" title="${esc(t("c")[c])}">${esc(c)}</span>`).join("");\nconst forP=r=>{if(r.binding==="leer")return`<span class="pc all">${t("allP")}</span>`;if(r.binding==="modell")return`<span class="pc mod" title="${esc(t("viaMod")+": "+r.modell+" · "+r.printers.join(", "))}">${esc(r.modell_kurz)}</span>`;const so=(r.sys_only||[]).map(x=>`<span class="pc sx" title="${esc(t("viaSysOnly"))}">${esc(x.replace(/^Bambu Lab /,"").replace(/ nozzle$/,""))}</span>`).join("");\n const tt=(r.tot||[]).map(x=>`<span class="pc tot" title="${esc(t("dead"))}">${esc(x)}</span>`).join("");\n if(!r.printers.length)return (so+tt)||\'<span class="empty">–</span>\';\n return so+tt+r.printers.map(p=>`<span class="pc${r.via[p]==="system"?" sys":""}${r.kal?" k":""}" title="${esc(r.via[p]==="system"?t("viaSys"):t("viaOwn"))}">${esc(p)}</span>`).join("")};\nconst COLS={\n filament:[["name",nm,r=>r.name],["vendor",r=>esc(r.v.filament_vendor),r=>r.v.filament_vendor],["type",r=>esc(r.v.filament_type),r=>r.v.filament_type],\n  ["for",forP,r=>r.printers.join()],["nozzle",r=>pair(r.v.nozzle_temperature,r.v.nozzle_temperature_initial_layer),r=>+g(r,"nozzle_temperature").split(",")[0],1],\n  ["bed",r=>pair(r.v.hot_plate_temp,r.v.textured_plate_temp),r=>+r.v.hot_plate_temp,1],["fan",r=>val(r.v.fan_min_speed)+"/"+val(r.v.fan_max_speed),r=>+g(r,"fan_min_speed").split(",")[0],1],\n  ["mvf",r=>val(r.v.filament_max_volumetric_speed),r=>+g(r,"filament_max_volumetric_speed").split(",")[0],1],\n  ["pa",r=>r.src==="studio"?(r.pa?`<span title="${esc(t("stuPA"))}">${esc(r.pa)}</span>`:`<span class="empty" title="${esc(t("stuNoPA"))}">–</span>`):g(r,"enable_pressure_advance").split(",")[0]==="1"?val(r.v.pressure_advance):`<span class="empty">${t("off")}</span>`,r=>r.src==="studio"?+(r.pa||0):+g(r,"pressure_advance").split(",")[0],1],\n  ["flow",r=>val(r.v.filament_flow_ratio),r=>+g(r,"filament_flow_ratio").split(",")[0],1],\n  ["shr",r=>pair(pct(r.v.filament_shrink),pct(r.v.filament_shrinkage_compensation_z)),r=>parseFloat(r.v.filament_shrink),1],\n  ["checks",ck,r=>r.checks.join()],["notes",r=>esc(r.notes),r=>r.notes]],\n process:[["name",nm,r=>r.name],["for",forP,r=>r.printers.join()],["lh",r=>val(r.v.layer_height),r=>+r.v.layer_height,1],\n  ["hole",r=>val(r.v.xy_hole_compensation),r=>+r.v.xy_hole_compensation,1],["cont",r=>val(r.v.xy_contour_compensation),r=>+r.v.xy_contour_compensation,1],\n  ["ef",r=>val(r.v.elefant_foot_compensation),r=>+r.v.elefant_foot_compensation,1],["checks",ck,r=>r.checks.join()],["notes",r=>esc(r.notes),r=>r.notes]],\n printer:[["name",nm,r=>r.name],["model",r=>esc(r.v.printer_model),r=>r.v.printer_model],["nd",r=>val(r.v.nozzle_diameter),r=>+r.v.nozzle_diameter,1],\n  ["base",r=>esc(r.inherits),r=>r.inherits],["nf",r=>r.nf,r=>r.nf,1],["np",r=>r.np,r=>r.np,1],["notes",r=>esc(r.notes),r=>r.notes]]};\nconst TYPES=["filament","filament","process","printer","changes"];\nfunction opts(sel,first,list){const v=sel.value;sel.innerHTML=`<option value="">${esc(first)}</option>`+list.map(x=>`<option>${esc(x)}</option>`).join("");sel.value=v}\nfunction filt(type){const fQ=$("fQ").value,fP=$("fP").value,fT=$("fT").value,fV=$("fV").value,fK=$("fK").value,fA=$("fA").checked,q=$("fS").value.toLowerCase();\n return D[type].filter(r=>{if(fQ&&(r.src||"orca")!==fQ)return false;if(type!=="printer"){if(fP&&!r.printers.includes(fP))return false;if(fK==="gk"&&r.kal)return false;if(fK==="kal"&&!r.kal)return false;if(fA&&!r.checks.length)return false}\n  else if(fP&&r.name!==fP)return false;\n  if(type==="filament"){if(fT&&r.v.filament_type!==fT)return false;if(fV&&r.v.filament_vendor!==fV)return false}\n  if(q&&!(r.name+" "+r.notes).toLowerCase().includes(q))return false;return true})}\nfunction render(){document.documentElement.lang=L;document.querySelectorAll("[data-t]").forEach(e=>e.textContent=t(e.dataset.t));\n document.querySelectorAll(".lang button").forEach(b=>b.classList.toggle("on",b.dataset.l===L));\n $("stand").textContent=t("stand")+" "+D.stand;$("eb").textContent="⚙ "+t("settings");\n const sq=$("fQ");if(D.studio&&D.studio.aktiv){sq.style.display="";const qv=sq.value;sq.innerHTML=`<option value="">${t("allSrc")}</option><option value="orca">Orca</option><option value="studio">Studio</option>`;sq.value=qv}else{sq.style.display="none";sq.value=""}$("rf").textContent="↻ "+t("refresh");$("fS").placeholder=t("search");$("dS").placeholder=t("search");\n opts($("fP"),t("allPr"),D.printer_names);opts($("fT"),t("allTy"),[...new Set(D.filament.map(r=>r.v.filament_type))].sort());\n opts($("fV"),t("allVe"),[...new Set(D.filament.map(r=>r.v.filament_vendor))].sort());\n const k=$("fK").value;$("fK").innerHTML=`<option value="">${t("all")}</option><option value="gk">${t("gk")}</option><option value="kal">${t("kal")}</option>`;$("fK").value=k;\n $("tabs").innerHTML=t("tabs").map((x,i)=>`<button class="${i===tab?"on":""}${i===4&&(D.aend||[]).length?" hl":""}" data-i="${i}">${x}${i===4&&(D.aend||[]).length?" ("+D.aend.length+")":""}</button>`).join("");\n $("ab").textContent=t("allSheets");\n const type=TYPES[tab];if(type==="changes"){renderCh();return}const rows=filt(type);let h="";\n if(tab===0){const ps=$("fP").value?[$("fP").value]:D.printer_names;\n  h=`<table class="mx"><thead><tr><th>${t("name")}</th>${ps.map(p=>`<th class="rot">${esc(p)}</th>`).join("")}</tr></thead><tbody>`+\n  rows.map(r=>`<tr data-n="${esc(r.name)}"><td>${nm(r)}</td>${ps.map(p=>`<td>${r.printers.includes(p)?(r.kal?\'<span class="K">K</span>\':\'<span class="dot">●</span>\'):""}</td>`).join("")}</tr>`).join("")+"</tbody></table>";\n }else{const cols=COLS[type];let rs=rows.slice();if(sortK!==null){const f=cols[sortK][2];rs.sort((a,b)=>{const x=f(a),y=f(b);return (x>y?1:x<y?-1:0)*sortD})}\n  h=`<table><thead><tr>${cols.map((c,i)=>`<th data-s="${i}">${t(c[0])}${sortK===i?(sortD>0?" ▲":" ▼"):""}</th>`).join("")}</tr></thead><tbody>`+\n  rs.map(r=>{VN=vnam(r);return`<tr data-n="${esc(r.name)}">${cols.map(c=>`<td class="${c[3]?"num":""}">${c[1](r)}</td>`).join("")}</tr>`}).join("")+"</tbody></table>"}\n $("main").innerHTML=`<div class="leg">${t("leg")} · ${t("legP")} · ${t("legM")}${D.studio&&D.studio.fehler?` · <span class="err">${t("stuErr")}: ${esc(D.studio.fehler)}</span>`:""}</div>`+h;cur&&det(cur.r,cur.type)}\nlet cur=null;\nfunction det(r,type){cur={r,type};VN=vnam(r);$("bs").textContent=t("sheet");$("bs").style.display=(type==="filament"&&HO)?"":"none";$("det").classList.add("open");$("dn").innerHTML=nm(r);\n const bt=r.binding?`${t("binding")}: ${esc(r.binding)} · `:"";\n $("dm").innerHTML=`${t("parent")}: ${esc(r.inherits)||"–"}${r.inherits?" ("+(r.parent_own?t("own"):t("sys"))+(r.parent_found?"":", "+t("nf_par"))+")":""}<br>${bt}${type!=="printer"?t("for")+": "+forP(r)+"<br>":""}${ck(r)}`;\n const q=$("dS").value.toLowerCase(),od=$("dD").checked,dm=Object.fromEntries(r.diff.map(x=>[x[0],x[2]]));\n $("db").innerHTML=Object.keys(r.v).sort().filter(k=>(!q||k.includes(q)||String(r.v[k]).toLowerCase().includes(q))&&(!od||k in dm)).map(k=>\n  `<tr class="${k in dm?"ch":""}"><td>${esc(k)}</td><td>${val(r.v[k])}${k in dm?`<div class="par">${t("inP")}: ${esc(dm[k])||"–"}</div>`:""}</td></tr>`).join("")}\ndocument.addEventListener("click",e=>{const l=e.target.closest(".lang button[data-l]");if(l){L=l.dataset.l;render();if(HO)window.orca.postMessage({cmd:"sprache",l:L});return}\n const b=e.target.closest(".tabs button");if(b){tab=+b.dataset.i;sortK=null;render();return}\n const s=e.target.closest("th[data-s]");if(s){const i=+s.dataset.s;sortD=sortK===i?-sortD:1;sortK=i;render();return}\n const tr=e.target.closest("main tbody tr[data-n]");if(tr){const type=TYPES[tab];if(cur&&cur.type===type&&cur.r.name===tr.dataset.n){$("det").classList.remove("open");cur=null;return}det(D[type].find(r=>r.name===tr.dataset.n),type)}});\n$("dx").onclick=()=>{$("det").classList.remove("open");cur=null};\n["fQ","fP","fT","fV","fK","fA"].forEach(i=>$(i).onchange=render);$("fS").oninput=render;$("dS").oninput=()=>cur&&det(cur.r,cur.type);$("dD").onchange=()=>cur&&det(cur.r,cur.type);\n/*BLATT*/\nconst SB={de:{gk:"Grundkalibrierung",mk:"Maßkalibrierung",noz:"Düse",bedS:"Bett glatt",bedT:"Bett Textur",ch:"Kammer",fan:"Lüfter",fanOff:"Lüfter aus",\nfanTh:"Schwellen",ovh:"Überhang-Lüfter",mvf:"MVF",pa:"PA",flow:"Flow",ret:"Rückzug",shrXY:"Schrumpf XY",shrZ:"Schrumpf Z",proc:"Prozess",lh:"Schichthöhe",\nlw:"Linienbreite außen / innen",lw1:"Linienbreite 1. Schicht",hole:"Loch-Korrektur",cont:"Kontur-Korrektur",ef:"Elefantenfuß",ws:"Wandreihenfolge",\npw:"Präzise Außenwand",notes:"Notizen",first:"1. Schicht",layers:"%n. Schicht",layersN:"Schicht 1–%n",printer:"Drucker",basis:"Basis",stand:"Stand",hotend:"Hotend",\nonly:"gilt nur für %h-Hotend",allN:"alle Düsen",made:"Erstellt",on:"an",offv:"aus",unk:"unklar",\nboth:"Standard-Hotend · (HF …) = High Flow",ws_io:"innen → außen",ws_oi:"außen → innen",ws_ioi:"innen–außen–innen"},\nen:{gk:"Base calibration",mk:"Dimensional calibration",noz:"Nozzle",bedS:"Bed smooth",bedT:"Bed textured",ch:"Chamber",fan:"Fan",fanOff:"Fan off",\nfanTh:"Thresholds",ovh:"Overhang fan",mvf:"MVS",pa:"PA",flow:"Flow",ret:"Retraction",shrXY:"Shrink XY",shrZ:"Shrink Z",proc:"Process",lh:"Layer height",\nlw:"Line width outer / inner",lw1:"Line width 1st layer",hole:"Hole compensation",cont:"Contour compensation",ef:"Elephant foot",ws:"Wall order",\npw:"Precise outer wall",notes:"Notes",first:"1st layer",layers:"layer %n",layersN:"layers 1–%n",printer:"Printer",basis:"Base",stand:"As of",hotend:"Hotend",\nonly:"valid only for %h hotend",allN:"all nozzles",made:"Created",on:"on",offv:"off",unk:"unclear",\nboth:"Standard hotend · (HF …) = high flow",ws_io:"inner → outer",ws_oi:"outer → inner",ws_ioi:"inner–outer–inner"}};\nfunction hotend(r){const p=vnam(r),m=/Hotend:\\s*(Standard|High\\s*Flow)/i.exec(r.notes||"");\n if(p.length<=1)return{i:0,n:p.length,lab:p[0]||""};\n if(!m)return{i:0,n:p.length,lab:""};const hf=/high/i.test(m[1]);const i=p.findIndex(x=>hf?/high/i.test(x):!/high/i.test(x));\n return{i:i<0?0:i,n:p.length,lab:hf?"High Flow":"Standard"}}\nfunction pk(s,i){s=String(s??"");if(s==="nil")return"";const a=s.split(",").map(x=>x.trim());if(i<0){const b=a.filter(x=>x&&x!=="nil");return b.length>1&&b[1]!==b[0]?b[0]+" (HF "+b[1]+")":(b[0]||"")}const x=(a[i]??a[0]);return x==="nil"?"":x}\nfunction blatt(r,f){const S=SB[L],h=hotend(r),i=(h.n>=2&&!h.lab&&!r.kal)?-1:h.i,v=r.v,P=k=>pk(v[k],i),E=x=>esc(x);\n const rows=[],row=(l,x)=>{if(x!==""&&x!=null)rows.push([l,x])};\n const temp=(a,b)=>{const x=P(a),y=P(b);if(!x)return"";return x+" °C"+(y&&y!==x?` · ${S.first} ${y} °C`:"")};\n row(S.noz,temp("nozzle_temperature","nozzle_temperature_initial_layer"));\n row(S.bedS,temp("hot_plate_temp","hot_plate_temp_initial_layer"));\n row(S.bedT,temp("textured_plate_temp","textured_plate_temp_initial_layer"));\n if(+P("chamber_temperature")>0)row(S.ch,P("chamber_temperature")+" °C");\n if(P("fan_min_speed"))row(S.fan,P("fan_min_speed")+"–"+P("fan_max_speed")+" %");\n if(+P("close_fan_the_first_x_layers")>0){const n=+P("close_fan_the_first_x_layers");row(S.fanOff,n===1?S.layers.replace("%n",1):S.layersN.replace("%n",n))}\n if(P("fan_cooling_layer_time"))row(S.fanTh,P("fan_cooling_layer_time")+" s / "+P("slow_down_layer_time")+" s");\n if(P("overhang_fan_speed"))row(S.ovh,P("overhang_fan_speed")+" %");\n if(P("filament_max_volumetric_speed"))row(S.mvf,P("filament_max_volumetric_speed")+" mm³/s");\n if(r.src==="studio"){if(r.pa)row(S.pa,r.pa+" (M900)")}else row(S.pa,pk(v.enable_pressure_advance,Math.max(i,0))==="1"?P("pressure_advance"):S.offv);\n row(S.flow,P("filament_flow_ratio"));\n const rl=P("filament_retraction_length"),rs=P("filament_retraction_speed"),rz=P("filament_z_hop");\n if(rl||rs||rz)row(S.ret,[rl&&rl+" mm",rs&&rs+" mm/s",rz&&"Z-Hop "+rz+" mm"].filter(Boolean).join(" · "));\n const gk=rows.splice(0);\n let proc=null;if(r.kal){const pn=(v.compatible_prints||"").split(" | ").filter(Boolean);proc=D.process.find(p=>(p.src||"orca")===(r.src||"orca")&&pn.includes(p.label||p.name))||null}\n if(r.kal){const sx=P("filament_shrink"),sz=P("filament_shrinkage_compensation_z");row(S.shrXY,sx);row(S.shrZ,sz);row(S.flow,P("filament_flow_ratio"));\n  if(proc){const q=proc.v,Q=k=>pk(q[k],0);row(S.proc,E(proc.label||proc.name));\n   row(S.lh,Q("layer_height")+" mm"+(Q("initial_layer_print_height")?` · ${S.first} ${Q("initial_layer_print_height")} mm`:""));\n   row(S.lw,Q("outer_wall_line_width")+" / "+Q("inner_wall_line_width")+" mm");row(S.lw1,Q("initial_layer_line_width")+" mm");\n   row(S.hole,Q("xy_hole_compensation")+" mm");row(S.cont,Q("xy_contour_compensation")+" mm");row(S.ef,Q("elefant_foot_compensation")+" mm");\n   const ws={"inner wall/outer wall":S.ws_io,"outer wall/inner wall":S.ws_oi,"inner-outer-inner wall":S.ws_ioi}[Q("wall_sequence")]||Q("wall_sequence");row(S.ws,ws);\n   row(S.pw,Q("precise_outer_wall")==="1"?S.on:S.offv)}}\n const mk=rows.splice(0);\n const nt=r.notes||"",bas=(/Basis:\\s*([^·]+)/i.exec(nt)||[])[1],std=(/Stand\\s*([\\d.]+)/i.exec(nt)||[])[1];\n const pr=r.binding==="modell"?r.modell_kurz+" ("+S.allN+")":r.printers.join(", ");\n const meta=[r.src==="studio"?"Bambu Studio":"",E(v.filament_vendor),E(v.filament_type),pr&&`${S.printer}: ${E(pr)}`,bas&&`${S.basis}: ${E(bas.trim())}`,std&&`${S.stand} ${E(std)}`].filter(Boolean).join(" · ");\n const hot=h.n>=2?(h.lab?S.only.replace("%h",h.lab):(r.kal?`${S.hotend}: ${S.unk}`:S.both)):"";\n const fl=[[f.f1_label,f.f1_wert],[f.f2_label,f.f2_wert]].filter(x=>(x[1]||"").trim()).map(x=>`<div><span>${E(x[0])}</span> ${E(x[1])}</div>`).join("");\n const tr=(a)=>a.map(x=>`<tr><td>${E(x[0])}</td><td>${x[1]}</td></tr>`).join(""),sec=(x,f)=>`<tr class="sec${f?" f":""}"><td colspan="2"><h2>${x}</h2></td></tr>`;\n const heute=new Date(),dd=x=>String(x).padStart(2,"0"),dat=`${dd(heute.getDate())}.${dd(heute.getMonth()+1)}.${String(heute.getFullYear()).slice(2)}`;\n return `<!DOCTYPE html><html lang="${L}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${E(r.label||r.name)}</title><style>\n@page{size:A4;margin:10mm}*{box-sizing:border-box}html,body{margin:0;background:#8a8f91}body{display:flex;justify-content:center;align-items:flex-start}\n.pg{width:794px;height:1123px;flex:none;background:#fff;color:#1d2224;font:15px/1.4 "Helvetica Neue",Arial,sans-serif;padding:42px 46px 30px;display:flex;flex-direction:column;transform-origin:top center;position:relative}\n.logo{position:absolute;top:36px;right:46px;line-height:0}\nh1{font-size:24px;margin:0 125px 4px 0;color:#0e6f78}.kal{display:inline-block;background:#0e6f78;color:#fff;font-size:12px;padding:1px 6px;border-radius:3px;vertical-align:4px;margin-left:6px}\n.meta{color:#5b6366;font-size:13px}.hot{margin-top:6px;font-weight:600;color:#b4621f;font-size:13px}\n.fl{display:flex;gap:28px;margin-top:10px;font-size:14px}.fl span{color:#5b6366}\nh2{font-size:12px;letter-spacing:1.2px;text-transform:uppercase;color:#0e6f78;border-bottom:2px solid #0e6f78;padding-bottom:3px;margin:22px 0 6px}\ntable{border-collapse:collapse;width:100%}td{padding:4px 0;border-bottom:1px solid #e3e6e7;vertical-align:top}td:first-child{color:#5b6366;width:1%;white-space:nowrap;text-align:right;padding-right:16px}td:last-child{text-align:left}tr.sec td{border-bottom:0;padding:0;font-family:"Helvetica Neue",Arial,sans-serif;text-align:left;white-space:normal;width:auto}tr.sec h2{margin:22px 0 6px}tr.sec.f h2{margin-top:18px}\ntd:last-child{font-family:Menlo,"IBM Plex Mono",monospace;font-size:14px}\n.nb{flex:1;display:flex;flex-direction:column;margin-top:22px;min-height:120px}.nb label{font-size:12px;letter-spacing:1.2px;text-transform:uppercase;color:#0e6f78}\ntextarea{flex:1;margin-top:4px;border:1px solid #c9cfd1;border-radius:4px;font:15px/1.5 "Helvetica Neue",Arial,sans-serif;padding:8px;resize:none;color:#1d2224;background:#fff}\n.ft{margin-top:10px;font-size:11px;color:#8a9296;display:flex;justify-content:space-between}\n@media print{html,body{background:#fff;height:auto!important;display:block}.pg{transform:none!important;width:auto;height:250mm;padding:0;overflow:hidden;break-inside:avoid;page-break-inside:avoid}.logo{top:0;right:0}}\n</style></head><body><div class="pg"><div class="logo"><svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 30 354 110" width="105" height="32.6" role="img" aria-label="rubi3dp.de"><rect x="0" y="127" width="329" height="9" rx="4.5" fill="rgb(14, 111, 120)"/><text x="0" y="122" textLength="290" lengthAdjust="spacingAndGlyphs" style="font:600 88px \'Barlow Condensed\',\'Arial Narrow\',Arial,sans-serif;fill:rgb(27, 37, 46)">rubi3dp<tspan style="fill:rgb(14, 111, 120)">.de</tspan></text><g><rect x="326" y="34" width="6" height="16" fill="rgb(27, 37, 46)"/><rect x="315" y="48" width="28" height="4" fill="rgb(27, 37, 46)"/><rect x="315" y="55" width="28" height="4" fill="rgb(27, 37, 46)"/><rect x="315" y="62" width="28" height="4" fill="rgb(27, 37, 46)"/><rect x="315" y="69" width="28" height="4" fill="rgb(27, 37, 46)"/><rect x="315" y="76" width="28" height="4" fill="rgb(27, 37, 46)"/><rect x="326" y="78" width="6" height="14" fill="rgb(27, 37, 46)"/><rect x="312" y="92" width="34" height="22" fill="rgb(27, 37, 46)"/><path d="M323 114h12l-4 12h-4z" fill="rgb(27, 37, 46)"/></g></svg></div>\n<h1>${E(r.label||r.name)}${r.kal?\'<span class="kal">kal</span>\':""}</h1><div class="meta">${meta}</div>${hot?`<div class="hot">${E(hot)}</div>`:""}${fl?`<div class="fl">${fl}</div>`:""}\n<table class="w">${sec(S.gk,true)}${tr(gk)}${mk.length?sec(S.mk)+tr(mk):""}</table>\n<div class="nb"><label>${S.notes}</label><textarea></textarea></div>\n<div class="ft"><span>${S.made} ${dat}</span><span>Preset Profiler ${E(D.version||"")}</span></div></div>\n<script>function fit(){var p=document.querySelector(\'.pg\'),s=Math.min(innerWidth/794,innerHeight/1123);p.style.transform=\'scale(\'+s+\')\';document.body.style.height=Math.ceil(1123*s)+\'px\'}addEventListener(\'resize\',fit);fit()<\\/script></body></html>`}\n/*DLG*/\nlet DLG=null;\nfunction dlg(html){$("dlg").innerHTML=`<div class="dbox">${html}</div>`;$("dlg").style.display="flex"}\nfunction dlgZu(){$("dlg").style.display="none";DLG=null}\nfunction blattStart(liste){DLG={liste,warte:1};dlg(`<p>${t("checking")}</p>`);window.orca.postMessage({cmd:"einst"})}\nfunction blattDialog(e){const liste=DLG.liste;D.einst=e;if(!e.blatt){dlg(`<p>${t("noFolder")}</p><p><button data-a="zu">OK</button></p>`);return}\n DLG={liste};\n dlg(`<b>${liste.length===1?esc(liste[0].name):t("allSheets")+" ("+liste.length+")"}</b>\n <p><label>${esc(labx(e.f1_label))}<br><input id="g1" value="${esc(e.f1_wert||"")}"></label></p>\n <p><label>${esc(labx(e.f2_label))}<br><input id="g2" value="${esc(e.f2_wert||"")}"></label></p>\n <p><button data-a="los">${t("create")}</button> <button data-a="zu">${t("cancel")}</button></p>`)}\nfunction labx(x){x=x||"";return L==="en"?({"Projekt":"Project"}[x]||x):x}\nfunction blattSenden(modus){const f={f1_label:labx(D.einst.f1_label),f1_wert:DLG.f1,f2_label:labx(D.einst.f2_label),f2_wert:DLG.f2};\n const dat=DLG.liste.map(r=>({name:r.name,html:blatt(r,f)}));dlg(`<p>${t("writing")}</p>`);window.orca.postMessage({cmd:"blatt_write",dateien:dat,modus})}\nfunction antw(a){if(a.cmd==="einst"&&DLG&&DLG.warte){blattDialog(a.einst);return}\n if(a.fehler==="kein_ordner"){dlg(`<p>${t("noFolder")}</p><p><button data-a="zu">OK</button></p>`);return}\n if(a.cmd==="blatt_check"&&DLG){const v=a.vorhanden||[],n=DLG.liste.length-v.length;\n  if(!v.length){blattSenden("alle");return}\n  if(DLG.liste.length===1){dlg(`<p>${t("exists1")}</p><p><button data-a="alle">${t("overwrite")}</button> <button data-a="zu">${t("cancel")}</button></p>`);return}\n  dlg(`<p>${t("existsN").replace("%v",v.length).replace("%n",n)}</p><p><button data-a="alle">${t("overwriteAll")}</button> <button data-a="neu">${t("onlyNew")}</button> <button data-a="zu">${t("cancel")}</button></p>`);return}\n if(a.cmd==="blatt_ok"){const w=a.verwaist||[];\n  dlg(`<p>${t("written").replace("%n",a.n||0)}${a.uebersprungen?" · "+t("skipped").replace("%n",a.uebersprungen):""}</p>\n  ${(a.fehler&&a.fehler.length)?`<p class="err">${esc(a.fehler.join("; "))}</p>`:""}\n  ${w.length?`<p>${t("orphans")}</p><ul>${w.map(x=>`<li>${esc(x)}</li>`).join("")}</ul>`:""}\n  <p><button data-a="zu">OK</button></p>`);DLG=null;return}\n if(a.fehler){dlg(`<p class="err">${esc(a.fehler)}</p><p><button data-a="zu">OK</button></p>`)}}\ndocument.addEventListener("click",e=>{const b=e.target.closest("#dlg button[data-a]");if(!b)return;const a=b.dataset.a;\n if(a==="zu"){dlgZu();return}\n if(a==="los"){DLG.f1=$("g1").value.trim();DLG.f2=$("g2").value.trim();dlg(`<p>${t("checking")}</p>`);window.orca.postMessage({cmd:"blatt_check",namen:DLG.liste.map(r=>r.name)});return}\n if(a==="alle"||a==="neu")blattSenden(a)});\n\nfunction renderCh(){const a=D.aend||[],s=D.aend_seit||"";let h="";\n if(!s&&!a.length){h=`<p class="leg">${t("firstRef")}</p>`}\n else if(!a.length){h=`<p class="leg">${t("noChanges")} ${esc(s)}</p>`}\n else{h=`<p class="leg">${a.length} · ${t("since")} ${esc(s)} ${HO?`<button class="btn" id="gs">${t("seen")}</button> <span class="leg">${t("seenHint")}</span>`:""}</p><table><thead><tr><th>${t("type")}</th><th>${t("prof")}</th><th>${t("param")}</th><th>${t("old")}</th><th>${t("new")}</th></tr></thead><tbody>`+\n  a.map(x=>`<tr><td>${esc(x[0])}</td><td>${esc(x[1])}</td><td>${x[2]?esc(x[2]):(x[4]==="neu"?t("ch_new"):t("ch_gone"))}</td><td>${x[2]?val(x[3]):""}</td><td>${x[2]?val(x[4]):""}</td></tr>`).join("")+"</tbody></table>"}\n h+=`<details style="margin-top:14px"><summary class="leg">Start-Log</summary><pre style="font:11px Menlo,monospace">${esc((D.startlog||[]).join("\\n")||"–")}</pre></details>`;\n $("main").innerHTML=h;const g=$("gs");if(g)g.onclick=()=>{g.disabled=true;window.orca.postMessage({cmd:"gesehen"})}}\nconst HO=typeof window.orca!=="undefined"&&window.orca.postMessage;\nif(HO){$("ab").style.display="";$("ab").onclick=()=>blattStart(D.filament.slice());$("bs").onclick=()=>cur&&blattStart([cur.r]);$("rf").style.display="";$("eb").style.display="";$("eb").onclick=()=>window.orca.postMessage({cmd:"einst_oeffnen"});$("rf").onclick=()=>{$("rf").disabled=true;window.orca.postMessage({cmd:"refresh"})};\n window.orca.onMessage(m=>{if(m&&m.antw){antw(m.antw);return}if(m&&m.data){const keep=cur&&cur.r.name,ty=cur&&cur.type;D=m.data;L=D.lang||L;cur=null;render();\n  if(keep){const r=D[ty].find(x=>x.name===keep);if(r)det(r,ty);else $("det").classList.remove("open")}}$("rf").disabled=false})}\nrender();\n</script></body></html>\n'
EINST_DATEI = "einstellungen.json"
STANDARD = {"zielordner": "", "sprache": "de", "kal_zusatz": "", "blattordner": "",
            "f1_label": "Name", "f1_wert": "", "f2_label": "Projekt", "f2_wert": "",
            "start_oeffnen": "0", "start_export": "0", "start_hinweis": "1", "studio": "0"}
REF_DATEI = "referenz.json"
RAUSCHEN = {"extruder_nozzle_stats"}  # interne Orca-Zähler, keine Einstellungen
BLATT_INDEX = "datenblaetter.json"
LADELOG = []
_panel = None
_einst_panel = None
_start_erledigt = False
EREIGNISLOG = []
_T0 = time.time()

# ---------------------------------------------------------------- Einstellungen

def _plugin_data():
    """Ordner orca_plugins/plugin_data – aus dem Installationsort, sonst Orca-Datenordner je System."""
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.basename(d) == "orca_plugins":
            return os.path.join(d, "plugin_data")
        oben = os.path.dirname(d)
        if oben == d:
            break
        d = oben
    if sys.platform.startswith("win"):
        basis = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "OrcaSlicer")
    elif sys.platform == "darwin":
        basis = os.path.expanduser("~/Library/Application Support/OrcaSlicer")
    else:
        basis = os.path.expanduser("~/.config/OrcaSlicer")
    return os.path.join(basis, "orca_plugins", "plugin_data")


def _ersatz_speicher():
    """Plugin-Datenordner, genau wie Orca ihn vergibt – auch wenn orca.host.plugin.storage()
    gerade nicht verfügbar ist (beim Laden, in Rückrufen der Fenster).
    - abonniert (Orca Cloud): orca_plugins/_subscribed/<Nutzer>/<Plugin>/… → plugin_data/_subscribed/<Nutzer>/<Plugin>
    - lokal installiert: plugin_data/<Dateiname ohne .py>"""
    d = os.path.dirname(os.path.abspath(__file__))
    teile = []
    while True:
        if os.path.basename(d) == "orca_plugins":
            break
        oben = os.path.dirname(d)
        if oben == d:
            teile = []
            break
        teile.insert(0, os.path.basename(d))
        d = oben
    if len(teile) >= 3 and teile[0] == "_subscribed":
        return os.path.join(_plugin_data(), *teile[:3])
    stamm = os.path.splitext(os.path.basename(__file__))[0]
    return os.path.join(_plugin_data(), stamm)


_SPEICHER = None


def pfad_pruefung():
    try:
        echt = str(orca.host.plugin.storage())
    except Exception as x:
        echt = "nicht verfügbar (" + type(x).__name__ + ")"
    ers = _ersatz_speicher()
    gleich = os.path.normpath(echt) == os.path.normpath(ers)
    return [f"Plugin-Datei: {os.path.abspath(__file__)}", f"Speicher (Orca): {echt}",
            f"Speicher (abgeleitet): {ers}", "Pfade gleich: " + ("ja" if gleich else "NEIN"),
            f"Speicher (benutzt): {speicher()}"]


def speicher():
    """Immer derselbe Ordner: einmal von Orca erfragt und gemerkt, sonst selbst berechnet."""
    global _SPEICHER
    if _SPEICHER:
        return _SPEICHER
    try:
        _SPEICHER = str(orca.host.plugin.storage())
        return _SPEICHER
    except Exception:
        return _ersatz_speicher()


ALT_NAMEN = ("preset_profiler", "profiluebersicht")  # frühere Datenordner – Einstellungen/Stand von dort übernehmen


def lesbar(pfad):
    """Datei im eigenen Ordner; fehlt sie, aus einem früheren Datenordner übernehmen (nur lesen)."""
    if os.path.exists(pfad):
        return pfad
    f = os.path.basename(pfad)
    for n in ALT_NAMEN:
        a = os.path.join(_plugin_data(), n, f)
        if os.path.normpath(a) != os.path.normpath(pfad) and os.path.exists(a):
            return a
    return pfad


def einst_lesen(ordner=None):
    e = dict(STANDARD)
    try:
        with open(lesbar(os.path.join(ordner or speicher(), EINST_DATEI)), encoding="utf-8") as fh:
            e.update({k: v for k, v in json.load(fh).items() if k in STANDARD})
    except FileNotFoundError:
        pass
    except Exception as x:
        LADELOG.append("Einstellungen lesen: " + repr(x))
    return e


def einst_schreiben(e):
    os.makedirs(speicher(), exist_ok=True)
    with open(os.path.join(speicher(), EINST_DATEI), "w", encoding="utf-8") as fh:
        json.dump(e, fh, ensure_ascii=False, indent=1)

# ---------------------------------------------------------------- Lesen

IDKEYS = {"inherits", "filament_settings_id", "print_settings_id", "printer_settings_id"}
NOTIZ = {"filament": "filament_notes", "process": "notes", "printer": "printer_notes"}


def unq(s):
    s = "" if s is None else str(s).strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return s


def liste(s):
    s = "" if s is None else str(s).strip()
    return [unq(x) for x in s.split(";") if unq(x)] if s else []


def werte(p):
    v = {}
    for k in p.config_keys():
        try:
            raw = p.config_value(k)
        except Exception:
            continue
        if k in ("compatible_printers", "compatible_prints"):
            v[k] = " | ".join(liste(raw))
            if str(raw or "").strip() and not liste(raw):
                v.setdefault("__leer", []).append(k)
        else:
            v[k] = unq(raw)
    return v


def json_lesen(pfad, ersatz):
    try:
        with open(lesbar(pfad), encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return ersatz
    except Exception as x:
        LADELOG.append(pfad + ": " + repr(x))
        return ersatz


def json_schreiben(pfad, obj):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False)


HOTEND_RE = re.compile(r"Hotend:\s*(Standard|High\s*Flow)", re.I)


def varianten(v):
    s = v.get("filament_extruder_variant", "") or ""
    return [x.strip().strip('"') for x in re.split(r'";"|,', s) if x.strip().strip('"')]


def duese(v):
    try:
        return float(str(v.get("nozzle_diameter", "")).split(",")[0])
    except Exception:
        return None


def sammlung(coll):
    eigene = []
    for i in range(coll.size()):
        p = coll.preset(i)
        try:
            if p.is_user():
                eigene.append(p)
        except Exception:
            pass
    return eigene


def zahl(x):
    try:
        return float(str(x).rstrip("%"))
    except Exception:
        return None


def weicht_ab(val, ref):
    return any(z is not None and abs(z - ref) > 1e-9 for z in (zahl(x) for x in str(val or "").split(",")))


MODELL_RE = re.compile(r'^\s*printer_model\s*==\s*"([^"]+)"\s*$')


def modell_kurz(m):
    for p in ("Bambu Lab ", "Qidi X-", "Qidi ", "Creality "):
        if m.startswith(p):
            m = m[len(p):]
    return m.replace(" ", "")


def ist_kal(name, zusatz):
    return bool(zusatz) and zusatz in name.split()

# ---------------------------------------------------------------- Bambu Studio (nur lesen)

STUDIO_TYP = {"printer": "machine", "filament": "filament", "process": "process"}
STUDIO_META = {"name", "from", "setting_id", "instantiation", "type", "version", "base_id",
               "updated_time", "user_id", "is_custom_defined"}
STUDIO_ZUSATZ = " (Studio)"
M900_RE = re.compile(r"^\s*M900\b[^\n]*?\bK\s*([-+]?\d*\.?\d+)", re.M | re.I)
_SYS_CACHE = {}  # Pfad -> (mtime, json) – Systemprofile nur einmal laden


def studio_ordner():
    if sys.platform.startswith("win"):
        return os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "BambuStudio")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/BambuStudio")
    return os.path.expanduser("~/.config/BambuStudio")


def _json_datei(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _sys_json(p):
    m = os.path.getmtime(p)
    c = _SYS_CACHE.get(p)
    if c and c[0] == m:
        return c[1]
    j = _json_datei(p)
    _SYS_CACHE[p] = (m, j)
    return j


def studio_wert(x):
    if x is None:
        return ""
    if isinstance(x, list):
        return ",".join("" if y is None else str(y) for y in x)
    return str(x)


class OrcaQuelle:
    src = "orca"

    def __init__(self):
        b = orca.host.preset_bundle()
        self.colls = {"printer": b.printers, "filament": b.filaments, "process": b.prints}
        self.roh = {typ: [(p.name, werte(p)) for p in sammlung(c)] for typ, c in self.colls.items()}
        self._sys, self._el = {}, {}

    def ist_systemdrucker(self, n):
        if n not in self._sys:
            try:
                p = self.colls["printer"].find_preset(n)
                self._sys[n] = p is not None and not p.is_user()
            except Exception:
                self._sys[n] = False
        return self._sys[n]

    def eltern(self, typ, name):
        key = (typ, name)
        if key not in self._el:
            p = self.colls[typ].find_preset(name) if name else None
            if p is not None:
                pv = werte(p); pv.pop("__leer", None)
                self._el[key] = (pv, bool(p.is_user()))
            else:
                self._el[key] = (None, False)
        return self._el[key]

    def prozess_gibt(self, n):
        try:
            return self.colls["process"].find_preset(n) is not None
        except Exception:
            return True


class StudioQuelle:
    """Eigene Profile aus dem Bambu-Studio-Ordner. Vererbung: eigene Profile (auch filament/base) vor Systemprofilen."""
    src = "studio"

    def __init__(self, basis):
        self.basis = basis
        user = os.path.join(basis, "user")
        if not os.path.isdir(basis):
            raise FileNotFoundError("Ordner nicht gefunden")
        konten = os.listdir(user) if os.path.isdir(user) else []  # PermissionError = keine Freigabe
        self.sysidx = {t: {} for t in STUDIO_TYP}
        self._voll = set()
        rueck = {v: k for k, v in STUDIO_TYP.items()}
        sysb = os.path.join(basis, "system")
        for wurzel, ordner, dateien in os.walk(sysb):
            ordner.sort(key=lambda x: (x != "BBL", x))
            teile = os.path.relpath(wurzel, sysb).split(os.sep)
            typ = next((rueck[x] for x in teile if x in rueck), None)
            if not typ:
                continue
            for d in dateien:
                if d.endswith(".json"):
                    self.sysidx[typ].setdefault(d[:-5], os.path.join(wurzel, d))
        self.user = {t: {} for t in STUDIO_TYP}
        for konto in sorted(konten):
            for typ, ord_ in STUDIO_TYP.items():
                tp = os.path.join(user, konto, ord_)
                for wurzel, _, dateien in os.walk(tp):
                    for d in dateien:
                        if not d.endswith(".json"):
                            continue
                        p = os.path.join(wurzel, d)
                        try:
                            j, m = _json_datei(p), os.path.getmtime(p)
                        except Exception as x:
                            LADELOG.append(f"Studio {d}: {type(x).__name__}")
                            continue
                        n = str(j.get("name") or d[:-5])
                        if n not in self.user[typ] or m > self.user[typ][n][0]:
                            self.user[typ][n] = (m, j)
        self.roh = {typ: [(n, self.werte(typ, n)) for n in self.user[typ]] for typ in STUDIO_TYP}

    def _vollscan(self, typ):
        self._voll.add(typ)
        for p in list(self.sysidx[typ].values()):
            try:
                n = _sys_json(p).get("name")
                if n:
                    self.sysidx[typ].setdefault(str(n), p)
            except Exception:
                pass

    def _json(self, typ, name):
        if name in self.user[typ]:
            return self.user[typ][name][1], True
        p = self.sysidx[typ].get(name)
        if p is None and typ not in self._voll:
            self._vollscan(typ)
            p = self.sysidx[typ].get(name)
        if p:
            try:
                return _sys_json(p), False
            except Exception:
                pass
        return None, False

    def _aufl(self, typ, name, tiefe=0):
        j, _ = self._json(typ, name)
        if j is None:
            return None
        erg = {}
        if tiefe < 15:
            par = j.get("inherits") or ""
            if par and par != name:
                erg.update(self._aufl(typ, par, tiefe + 1) or {})
            inc = j.get("include") or []
            for x in (inc if isinstance(inc, list) else [inc]):
                erg.update(self._aufl(typ, str(x), tiefe + 1) or {})
        erg.update(j)
        return erg

    def _werte_aus(self, roh, eigen):
        v = {}
        for k, x in roh.items():
            if k in STUDIO_META:
                continue
            if k in ("compatible_printers", "compatible_prints"):
                l = [str(y) for y in (x if isinstance(x, list) else ([x] if x else [])) if y is not None]
                v[k] = " | ".join(y for y in l if y)
                if l and not any(l):
                    v.setdefault("__leer", []).append(k)
            else:
                v[k] = studio_wert(x)
        v["inherits"] = str(eigen.get("inherits") or "")
        return v

    def werte(self, typ, name):
        return self._werte_aus(self._aufl(typ, name) or {}, self.user[typ][name][1])

    def ist_systemdrucker(self, n):
        if n in self.sysidx["printer"]:
            return True
        if "printer" not in self._voll:
            self._vollscan("printer")
        return n in self.sysidx["printer"]

    def eltern(self, typ, name):
        if not name:
            return None, False
        j, eigen = self._json(typ, name)
        if j is None:
            return None, False
        pv = self._werte_aus(self._aufl(typ, name) or {}, j)
        pv.pop("__leer", None)
        return pv, eigen

    def prozess_gibt(self, n):
        return self._json("process", n)[0] is not None



def verarbeiten(q, e):
    """Zeilen einer Quelle (Orca oder Studio) aufbauen; Bindungen nur gegen die Drucker derselben Quelle."""
    roh = q.roh
    own_pr = [n for n, _ in roh["printer"]]
    sys_of, modell_of, pinfo = {}, {}, {}
    for n, v in roh["printer"]:
        modell_of[n] = v.get("printer_model", "")
        pinfo[n] = (modell_kurz(v.get("printer_model", "")), duese(v))
        sys_of.setdefault(v.get("inherits", ""), []).append(n)
    zus = (e.get("kal_zusatz") or "").strip()
    ist_systemdrucker, eltern = q.ist_systemdrucker, q.eltern
    out = {"printer": [], "filament": [], "process": []}

    for typ in ("filament", "process", "printer"):
        for name, v in roh[typ]:
            leer = v.pop("__leer", [])
            par = v.get("inherits", "")
            pv, par_own = eltern(typ, par)
            diff = []
            if pv is not None:
                for k in sorted(set(v) | set(pv)):
                    if k in IDKEYS:
                        continue
                    if v.get(k, "") != pv.get(k, ""):
                        diff.append([k, v.get(k, ""), pv.get(k, "")])
            r = {"name": name, "label": name, "src": q.src, "kal": False, "inherits": par, "parent_own": par_own, "parent_found": pv is not None,
                 "printers": [], "via": {}, "binding": "", "checks": [], "notes": v.get(NOTIZ[typ], ""), "v": v, "diff": diff}
            if typ != "printer":
                cp = [x for x in v.get("compatible_printers", "").split(" | ") if x]
                pr, kinds, via = [], set(), {}
                cond = v.get("compatible_printers_condition", "").replace('\\"', '"').strip()
                mm = MODELL_RE.match(cond) if (cond and not cp) else None
                modell = mm.group(1) if mm else ""
                if modell:
                    pr, binding = [n for n in own_pr if modell_of.get(n) == modell], "modell"
                    for n in pr: via[n] = "modell"
                elif not cp:
                    pr, binding = list(own_pr), "leer"
                else:
                    for x in cp:
                        if x in own_pr:
                            pr.append(x); kinds.add("eigen"); via[x] = "eigen"
                        else:
                            kinds.add("system")
                            for y in sys_of.get(x, []):
                                pr.append(y); via.setdefault(y, "system")
                    binding = "gemischt" if len(kinds) > 1 else kinds.pop()
                pr = sorted(set(pr))
                sys_only, tot = [], []
                for x in cp:
                    if x in own_pr or sys_of.get(x):
                        continue
                    (sys_only if ist_systemdrucker(x) else tot).append(x)
                kal = ist_kal(name, zus)
                if typ == "filament":
                    kw = weicht_ab(v.get("filament_shrink"), 100) or weicht_ab(v.get("filament_shrinkage_compensation_z"), 100)
                else:
                    kw = weicht_ab(v.get("xy_hole_compensation"), 0) or weicht_ab(v.get("xy_contour_compensation"), 0)
                ch = []
                if not cp and not modell: ch.append("B0")
                if kal and len(pr) > 1: ch.append("K2")
                if not pr and not (q.src == "studio" and sys_only): ch.append("V")
                if kw: ch.append("KW")
                if zus and kal and not kw: ch.append("K?")
                if zus and kw and not kal: ch.append("KN")
                if cond and not modell: ch.append("BD")
                if tot: ch.append("BT")
                if "compatible_prints" in leer or "compatible_printers" in leer: ch.append("PL")
                if typ == "filament":
                    for pn in [x for x in v.get("compatible_prints", "").split(" | ") if x]:
                        if not q.prozess_gibt(pn):
                            ch.append("KP"); break
                    var = varianten(v)
                    hm = HOTEND_RE.search(v.get("filament_notes", "") or "")
                    if kal and len(var) >= 2 and not hm: ch.append("HU")
                    if hm and len(var) == 1:
                        soll = "high" if "high" in hm.group(1).lower() else "standard"
                        if soll not in var[0].lower(): ch.append("HW")
                if binding in ("eigen", "system", "gemischt", "modell"):
                    kurz_set = {k for k, _ in pinfo.values() if k}
                    tok = name.split()
                    for i, tk in enumerate(tok):
                        if tk in kurz_set:
                            nz = None
                            if i + 1 < len(tok) and re.match(r"^\d+[.,]\d+$", tok[i + 1]):
                                nz = float(tok[i + 1].replace(",", "."))
                            ok = any(pinfo.get(p, ("", None))[0] == tk and (nz is None or binding == "modell"
                                     or (pinfo[p][1] is not None and abs(pinfo[p][1] - nz) < 1e-6)) for p in pr)
                            if binding == "modell" and nz is not None: ok = False
                            if not ok: ch.append("NB")
                            break
                if typ == "filament" and q.src == "studio":
                    m9 = M900_RE.search(v.get("filament_start_gcode", "") or "")
                    r["pa"] = m9.group(1) if m9 else ""
                r.update(printers=pr, via=via, binding=binding, kal=kal, checks=ch, sys_only=sys_only, tot=tot,
                         modell=modell, modell_kurz=modell_kurz(modell) if modell else "")
            out[typ].append(r)
    return out, own_pr


def daten_sammeln(e):
    t0 = time.time()
    out, own_pr = verarbeiten(OrcaQuelle(), e)
    studio = {"aktiv": str(e.get("studio", "0")) == "1", "n": 0, "fehler": ""}
    if studio["aktiv"]:
        try:
            so, spr = verarbeiten(StudioQuelle(studio_ordner()), e)
            umb = lambda n: n + STUDIO_ZUSATZ
            for typ in so:
                for r in so[typ]:
                    r["name"] = umb(r["name"])
                    r["printers"] = [umb(x) for x in r["printers"]]
                    r["via"] = {umb(k): x for k, x in r["via"].items()}
                    out[typ].append(r)
                    studio["n"] += 1
            own_pr = own_pr + [umb(x) for x in spr]
        except PermissionError:
            studio["fehler"] = "kein Zugriff – Orca neu starten und Abfrage bestätigen"
        except Exception as x:
            studio["fehler"] = type(x).__name__ + (": " + str(x) if str(x) else "")
            LADELOG.append("Studio: " + traceback.format_exc(limit=3))
    for r in out["printer"]:
        r["nf"] = sum(r["name"] in x["printers"] for x in out["filament"])
        r["np"] = sum(r["name"] in x["printers"] for x in out["process"])
    for typ in out:
        out[typ].sort(key=lambda r: r["name"].lower())
    out["printer_names"] = sorted(own_pr)
    out["stand"] = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    out["lang"] = e.get("sprache", "de")
    out["dauer"] = round(time.time() - t0, 2)
    out["version"] = VERSION
    out["studio"] = studio
    out["einst"] = {k: e.get(k, STANDARD[k]) for k in ("f1_label", "f1_wert", "f2_label", "f2_wert")}
    out["einst"]["blatt"] = bool(e.get("blattordner"))
    return out


def schnappschuss(d):
    return {typ: {r["name"]: r["v"] for r in d[typ]} for typ in ("printer", "filament", "process")}


def aenderungen(d):
    snap = schnappschuss(d)
    pfad = os.path.join(speicher(), REF_DATEI)
    ref = json_lesen(pfad, None)
    if ref is None:
        try:
            snap["stand"] = d["stand"]
            json_schreiben(pfad, snap)
        except Exception as x:
            LADELOG.append("Referenz: " + repr(x))
        return [], ""
    out = []
    for typ in ("printer", "filament", "process"):
        a, b = ref.get(typ, {}), snap[typ]
        for n in sorted(set(a) | set(b), key=str.lower):
            if n not in a:
                out.append([typ, n, "", "", "neu"])
            elif n not in b:
                out.append([typ, n, "", "entfernt", ""])
            else:
                for k in sorted(set(a[n]) | set(b[n])):
                    if k in RAUSCHEN:
                        continue
                    if a[n].get(k, "") != b[n].get(k, ""):
                        out.append([typ, n, k, a[n].get(k, ""), b[n].get(k, "")])
    return out, ref.get("stand", "") if isinstance(ref.get("stand", ""), str) else ""


def referenz_setzen(d):
    snap = schnappschuss(d)
    snap["stand"] = d["stand"]
    json_schreiben(os.path.join(speicher(), REF_DATEI), snap)

# ---------------------------------------------------------------- Schreiben

FEST = ["name", "source", "kal", "inherits", "parent_own", "printers", "binding", "checks", "notes"]
DATEI = {"printer": "drucker.csv", "filament": "filament.csv", "process": "prozess.csv"}


def csv_text(rows, sep):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=sep, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
    for row in rows:
        w.writerow(row)
    return buf.getvalue()


def dateien(d, e):
    sep = ";" if e.get("sprache", "de") == "de" else ","
    f = {}
    for typ, fn in DATEI.items():
        keys = sorted({k for r in d[typ] for k in r["v"]} - {"inherits", "source"})
        rows = [FEST + keys]
        for r in d[typ]:
            rows.append([r["name"], r.get("src", "orca"), "1" if r["kal"] else "0", r["inherits"], "1" if r["parent_own"] else "0",
                         " | ".join(r["printers"]), r["binding"], " ".join(r["checks"]), r["notes"]]
                        + [r["v"].get(k, "") for k in keys])
        f[fn] = csv_text(rows, sep)
    rows = [["type", "name", "parameter", "value", "parent_value", "parent", "parent_own"]]
    for typ in ("printer", "filament", "process"):
        for r in d[typ]:
            for k, a, b in r["diff"]:
                rows.append([typ, r["name"], k, a, b, r["inherits"], "1" if r["parent_own"] else "0"])
    f["unterschiede.csv"] = csv_text(rows, sep)
    f["uebersicht.html"] = html(d)
    return f


def html(d):
    return TEMPLATE.replace("/*DATA*/", json.dumps(d, ensure_ascii=False).replace("</", "<\\/"))


def sammeln(e):
    d = daten_sammeln(e)
    d["startlog"] = EREIGNISLOG[:] + LADELOG[-10:] + pfad_pruefung()
    try:
        d["aend"], d["aend_seit"] = aenderungen(d)
    except Exception:
        d["aend"], d["aend_seit"] = [], ""
        LADELOG.append("Änderungen: " + traceback.format_exc())
    return d


def exportieren(e, d=None):
    if d is None:
        d = sammeln(e)
    f = dateien(d, e)
    ziele = [speicher()]
    if e.get("zielordner"):
        ziele.append(e["zielordner"])
    fehler = []
    for z in ziele:
        for fn, txt in f.items():
            try:
                with open(os.path.join(z, fn), "w", encoding="utf-8") as fh:
                    fh.write(("\ufeff" + txt) if fn.endswith(".csv") else txt)
            except Exception as x:
                fehler.append(f"{z}/{fn}: {type(x).__name__}")
                break
    return d, ziele, fehler

# ---------------------------------------------------------------- Fenster

EINST_HTML = """<!DOCTYPE html><html><body style="padding:12px">
<b id="t1"></b>
<p id="hp" style="color:var(--orca-muted);font-size:11px;margin:4px 0 0"></p>
<p><label id="lz"></label><br><input id="z" style="width:100%"></p>
<p><label id="lk"></label><br><input id="k" style="width:90px"></p>
<p><label id="ls"></label><br><select id="s"><option value="de">Deutsch</option><option value="en">English</option></select></p>
<p><label id="lb"></label><br><input id="bo" style="width:100%"></p>
<p><label><input type="checkbox" id="so"> <span id="lso"></span></label><br><label><input type="checkbox" id="se"> <span id="lse"></span></label><br><label><input type="checkbox" id="sh"> <span id="lsh"></span></label><br><label><input type="checkbox" id="st"> <span id="lst"></span></label></p>
<p><label id="lf"></label><br><input id="f1l" style="width:35%"> <input id="f1w" style="width:60%"><br><input id="f2l" style="width:35%"> <input id="f2w" style="width:60%"></p>
<p><button id="b"></button></p><p id="r" style="color:var(--orca-muted)"></p>
<script>
const E=__E__;const T={de:{t1:"Einstellungen",lz:"Zielordner (leer = nur Plugin-Ordner)",lk:"kal-Zusatz im Profilnamen (leer = aus)",ls:"Sprache",b:"Speichern",lb:"Datenblatt-Ordner",lf:"Datenblatt-Felder (Beschriftung · Vorgabe)",lso:"Beim Start von Orca öffnen",lse:"Beim Start exportieren",lsh:"Beim Start auf geänderte Profile hinweisen",lst:"Bambu-Studio-Profile einlesen",hp:"Orca bietet Plugins keine Ordnerauswahl – Pfad bitte einfügen. Mac: Ordner im Finder markieren, ⌥⌘C. Windows: Ordner markieren, Strg+Umschalt+C."},
en:{t1:"Settings",lz:"Target folder (empty = plugin folder only)",lk:"Calibration tag in profile name (empty = off)",ls:"Language",b:"Save",lb:"Data sheet folder",lf:"Data sheet fields (label · default)",lso:"Open when Orca starts",lse:"Export when Orca starts",lsh:"Notify about changed profiles at start",lst:"Read Bambu Studio presets",hp:"Orca offers plugins no folder picker – please paste the path. Mac: select folder in Finder, ⌥⌘C. Windows: select folder, Ctrl+Shift+C."}};
function lab(){const L=document.getElementById('s').value;for(const k in T[L])document.getElementById(k).textContent=T[L][k]}
document.getElementById('z').value=E.zielordner;document.getElementById('k').value=E.kal_zusatz;document.getElementById('s').value=E.sprache;lab();
for(const k of ["f1_label","f1_wert","f2_label","f2_wert"])document.getElementById({f1_label:"f1l",f1_wert:"f1w",f2_label:"f2l",f2_wert:"f2w"}[k]).value=E[k];
document.getElementById('bo').value=E.blattordner;
document.getElementById('so').checked=E.start_oeffnen==="1";document.getElementById('se').checked=E.start_export==="1";document.getElementById('sh').checked=E.start_hinweis==="1";document.getElementById('st').checked=E.studio==="1";
document.getElementById('s').onchange=lab;
document.getElementById('b').onclick=()=>orca.postMessage({zielordner:document.getElementById('z').value.trim().replace(/\\/+$/,''),
 kal_zusatz:document.getElementById('k').value.trim(),sprache:document.getElementById('s').value,
 blattordner:document.getElementById('bo').value.trim().replace(/\\/+$/,''),
 f1_label:document.getElementById('f1l').value.trim(),f1_wert:document.getElementById('f1w').value.trim(),
 f2_label:document.getElementById('f2l').value.trim(),f2_wert:document.getElementById('f2w').value.trim(),
 start_oeffnen:document.getElementById('so').checked?"1":"0",start_export:document.getElementById('se').checked?"1":"0",start_hinweis:document.getElementById('sh').checked?"1":"0",studio:document.getElementById('st').checked?"1":"0"});
orca.onMessage(d=>{document.getElementById('r').textContent=d.antwort});
</script></body></html>"""


def panel_post(d):
    try:
        if _panel is not None and _panel.is_open():
            _panel.post({"data": d})
    except Exception:
        pass


def panel_antwort(a):
    try:
        if _panel is not None and _panel.is_open():
            _panel.post({"antw": a})
    except Exception:
        pass


def dateiname(n):
    return re.sub(r'[\\/:*?"<>|]', "_", n).strip() + ".html"


def blatt_check(e, namen):
    o = e.get("blattordner", "")
    if not o:
        return {"cmd": "blatt_check", "fehler": "kein_ordner"}
    vorh = [n for n in namen if os.path.exists(os.path.join(o, dateiname(n)))]
    return {"cmd": "blatt_check", "vorhanden": vorh, "namen": namen}


def blatt_schreiben(e, dateien_, modus):
    o = e.get("blattordner", "")
    if not o:
        return {"cmd": "blatt_ok", "fehler": "kein_ordner"}
    idx_pfad = os.path.join(speicher(), BLATT_INDEX)
    idx = set(json_lesen(idx_pfad, []))
    n_ok, uebersp, fehler = 0, 0, []
    for f in dateien_:
        pfad = os.path.join(o, dateiname(f["name"]))
        if modus == "neu" and os.path.exists(pfad):
            uebersp += 1
            continue
        try:
            with open(pfad, "w", encoding="utf-8") as fh:
                fh.write(f["html"])
            n_ok += 1
            idx.add(f["name"])
        except Exception as x:
            fehler.append(f"{f['name']}: {type(x).__name__}")
    try:
        aktuell = {r["name"] for r in daten_sammeln(e)["filament"]}
    except Exception:
        aktuell = set(idx)
    verwaist = sorted(n for n in idx if n not in aktuell and os.path.exists(os.path.join(o, dateiname(n))))
    idx = {n for n in idx if os.path.exists(os.path.join(o, dateiname(n)))}
    try:
        json_schreiben(idx_pfad, sorted(idx))
    except Exception as x:
        fehler.append("Index: " + type(x).__name__)
    return {"cmd": "blatt_ok", "n": n_ok, "uebersprungen": uebersp, "fehler": fehler,
            "verwaist": [dateiname(n) for n in verwaist]}


def panel_nachricht(m):
    if not isinstance(m, dict):
        return
    c = m.get("cmd")
    try:
        if c == "refresh":
            d, _, _ = exportieren(einst_lesen())
            panel_post(d)
        elif c == "gesehen":
            e = einst_lesen()
            referenz_setzen(daten_sammeln(e))
            d, _, _ = exportieren(e)
            panel_post(d)
        elif c == "einst":
            e = einst_lesen()
            ei = {k: e.get(k, STANDARD[k]) for k in ("f1_label", "f1_wert", "f2_label", "f2_wert")}
            ei["blatt"] = bool(e.get("blattordner"))
            panel_antwort({"cmd": "einst", "einst": ei})
        elif c == "sprache":
            l = m.get("l")
            e = einst_lesen()
            if l in ("de", "en") and e.get("sprache") != l:
                e["sprache"] = l
                einst_schreiben(e)
        elif c == "einst_oeffnen":
            try:
                einst_fenster()
            except Exception:
                LADELOG.append("Einstellungen öffnen: " + traceback.format_exc())
                de = einst_lesen().get("sprache", "de") == "de"
                panel_antwort({"cmd": c, "fehler": "Einstellungen bitte über das Menü öffnen: Plugins › Preset Profiler – Einstellungen."
                               if de else "Please open the settings via the menu: Plugins › Preset Profiler – Settings."})
        elif c == "blatt_check":
            panel_antwort(blatt_check(einst_lesen(), list(m.get("namen", []))))
        elif c == "blatt_write":
            panel_antwort(blatt_schreiben(einst_lesen(), list(m.get("dateien", [])), m.get("modus", "alle")))
    except Exception:
        LADELOG.append(f"Befehl {c}: " + traceback.format_exc())
        panel_antwort({"cmd": c, "fehler": traceback.format_exc(limit=2)})


def panel_oeffnen(d):
    global _panel
    if _panel is not None and _panel.is_open():
        _panel.post({"data": d})
        _panel.show()
    else:
        _panel = orca.host.ui.create_dock_panel(html=html(d), title="Preset Profiler", width=1200, height=420,
                                                on_message=panel_nachricht, on_close=lambda: None, dock="bottom")
        _panel.show()


def hinweis(text):
    for kw in ({"title": "Preset Profiler", "buttons": "ok", "icon": "info"}, {"title": "Preset Profiler", "buttons": "ok"}):
        try:
            orca.host.ui.message(text, **kw)
            return True
        except TypeError:
            continue
        except Exception:
            LADELOG.append("Hinweis: " + traceback.format_exc())
            return False
    LADELOG.append("Hinweis: keine passende Aufrufform")
    return False


START_EREIGNISSE = tuple(getattr(orca.LifecycleEvent, n) for n in ("NewProject", "ProjectOpened", "PresetSelected", "PlateSelected")
                         if hasattr(getattr(orca, "LifecycleEvent", None), n))


def beim_start():
    e = einst_lesen()
    an = lambda k: str(e.get(k, STANDARD[k])) == "1"
    if not (an("start_oeffnen") or an("start_export") or an("start_hinweis")):
        return
    d = sammeln(e)
    if an("start_export"):
        exportieren(e, d)
    hin = an("start_hinweis") and bool(d.get("aend"))
    if an("start_oeffnen"):
        if hin:
            d["start_tab"] = "changes"
        panel_oeffnen(d)
    elif hin:
        n = len(d["aend"])
        de = e.get("sprache", "de") == "de"
        hinweis(f"{n} Änderung(en) an Profilen seit {d.get('aend_seit') or 'dem letzten Stand'}.\nDetails: Preset Profiler › Reiter „Änderungen“."
                if de else f"{n} profile change(s) since {d.get('aend_seit') or 'last state'}.\nDetails: Preset Profiler › tab “Changes”.")


class Uebersicht(orca.script.ScriptPluginCapabilityBase):
    def get_name(self):
        return "Preset Profiler"

    def execute(self):
        global _panel
        try:
            e = einst_lesen()
            d, ziele, fehler = exportieren(e)
            panel_oeffnen(d)
            msg = f"{len(d['filament'])} Filament · {len(d['process'])} Prozess · {len(d['printer'])} Drucker · {d['dauer']} s"
            if d.get("studio", {}).get("aktiv"):
                msg += f" · Studio {d['studio']['n']}" + (" (" + d["studio"]["fehler"] + ")" if d["studio"]["fehler"] else "")
            if fehler:
                msg += " · Fehler: " + "; ".join(fehler)
            return orca.ExecutionResult.success(msg)
        except Exception:
            orca.host.ui.message(traceback.format_exc(), title="Preset Profiler", buttons="ok", icon="error")
            return orca.ExecutionResult.success("Fehler – siehe Meldung")

    def on_lifecycle_event(self, event, ctx):
        global _start_erledigt
        if len(EREIGNISLOG) < 40:
            EREIGNISLOG.append(f"{time.time() - _T0:6.1f} s  {event}")
        if not _start_erledigt and event != orca.LifecycleEvent.PresetSaved:
            _start_erledigt = True
            try:
                beim_start()
                EREIGNISLOG.append("→ Start-Aktion ausgeführt")
            except Exception:
                LADELOG.append("Start: " + traceback.format_exc())
        try:
            if event == orca.LifecycleEvent.PresetSaved:
                d, _, _ = exportieren(einst_lesen())
                panel_post(d)
        except Exception:
            LADELOG.append("Export beim Speichern: " + traceback.format_exc())


class Einstellungen(orca.script.ScriptPluginCapabilityBase):
    def get_name(self):
        try:
            return "Preset Profiler – Einstellungen" if einst_lesen(_ersatz_speicher()).get("sprache", "de") == "de" else "Preset Profiler – Settings"
        except Exception:
            return "Preset Profiler – Einstellungen"

    def execute(self):
        einst_fenster()
        return orca.ExecutionResult.success("Einstellungen geöffnet")


def einst_fenster():
    global _einst_panel
    e = einst_lesen()
    def nachricht(m):
        try:
            neu = {k: str(m.get(k, STANDARD[k])) for k in STANDARD}
            if neu["sprache"] not in ("de", "en"):
                neu["sprache"] = "de"
            alt = einst_lesen()
            einst_schreiben(neu)
            de = neu["sprache"] == "de"
            a = "Gespeichert." if de else "Saved."
            if neu["zielordner"] != alt["zielordner"] or neu["blattordner"] != alt["blattordner"] or neu["studio"] != alt["studio"]:
                a += " Gilt nach Neustart von OrcaSlicer." if de else " Applies after restarting OrcaSlicer."
            try:
                panel_post(sammeln(neu))
            except Exception:
                LADELOG.append("Übersicht nach Speichern: " + traceback.format_exc())
        except Exception as x:
            a = "FEHLER: " + repr(x)
        try:
            _einst_panel.post({"antwort": a})
        except Exception:
            pass

    try:
        if _einst_panel is not None and _einst_panel.is_open():
            _einst_panel.close()
    except Exception:
        pass
    _einst_panel = orca.host.ui.create_dock_panel(html=EINST_HTML.replace("__E__", json.dumps(e, ensure_ascii=False)),
                                                  title="Preset Profiler", width=440, height=570,
                                                  on_message=nachricht, on_close=lambda: None, dock="right")
    _einst_panel.show()


@orca.plugin
class PresetProfilerPlugin(orca.base):
    def register_capabilities(self):
        try:
            e0 = einst_lesen(_ersatz_speicher())
            ordner = [x for x in (e0.get("zielordner", ""), e0.get("blattordner", "")) if x]
            kw = {}
            if ordner:
                kw["fs_readwrite"] = [x + "/*" for x in dict.fromkeys(ordner)]
            if str(e0.get("studio", "0")) == "1":
                kw["fs_read"] = [studio_ordner() + "/*"]
            if kw:
                orca.request_permissions(**kw)
        except Exception:
            LADELOG.append("Zielordner anmelden: " + traceback.format_exc())
        orca.register_capability(Uebersicht)
        orca.register_capability(Einstellungen)
